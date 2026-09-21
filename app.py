"""Panel del Agente de Bienestar Preventivo.  Ejecutar:  streamlit run app.py"""

import os
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from agente import analisis, campanas, premios
from agente.catalogo import CHEQUEOS
from agente.crm import CRM, CRMLocal, ErrorCRM

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Agente de Bienestar Preventivo", page_icon="🩺", layout="wide")


def secreto(clave):
    try:
        if clave in st.secrets:
            return st.secrets[clave]
    except Exception:  # no hay secrets.toml: se usan variables de entorno
        pass
    return os.environ.get(clave)


def asegurados_de_prueba():
    return pd.read_csv(DATA / "asegurados.csv").to_dict("records")


# --- Conexión al CRM ------------------------------------------------------------

def obtener_crm():
    if "crm" in st.session_state:
        return st.session_state.crm, st.session_state.modo
    claves = [secreto(k) for k in ("NOTION_TOKEN", "NOTION_DB_ASEGURADOS", "NOTION_DB_CAMPANAS", "NOTION_DB_CHEQUEOS")]
    crm, modo = None, "local"
    if all(claves):
        try:
            candidato = CRM(*claves)
            problemas = candidato.verificar()
            if problemas:
                st.session_state.problemas_notion = problemas
            else:
                crm, modo = candidato, "notion"
        except Exception as e:
            st.session_state.problemas_notion = [str(e)]
    if crm is None:
        crm = CRMLocal()
        crm.reiniciar(asegurados_de_prueba())
    st.session_state.crm, st.session_state.modo = crm, modo
    return crm, modo


crm, modo = obtener_crm()
groq_key, groq_modelo = secreto("GROQ_API_KEY"), secreto("GROQ_MODEL")

if "feed" not in st.session_state:  # lo que el hospital va reportando
    st.session_state.feed = pd.read_csv(DATA / "chequeos.csv").to_dict("records")

# --- Barra lateral --------------------------------------------------------------

with st.sidebar:
    st.header("Estado del agente")
    if modo == "notion":
        st.success("CRM: conectado a Notion")
        if url := secreto("NOTION_URL_PUBLICA"):
            st.link_button("Ver el CRM en Notion", url, width="stretch")
    else:
        st.warning("CRM: modo local (en memoria)")
        for p in st.session_state.get("problemas_notion", []):
            st.caption(f"⚠️ {p}")
    st.write("IA: " + ("✅ Groq configurado" if groq_key else "⚠️ sin clave, se usarán plantillas"))

    st.divider()
    if st.button("Reiniciar demostración", width="stretch",
                 help="Borra campañas y premios, y vuelve a cargar los 15 asegurados de prueba."):
        with st.spinner("Reiniciando el CRM..."):
            crm.reiniciar(asegurados_de_prueba())
        for k in ("feed", "propuestas", "decisiones"):
            st.session_state.pop(k, None)
        st.rerun()
    st.caption("Todos los datos son **ficticios**, generados para esta demostración.")

# --- Encabezado -----------------------------------------------------------------

st.title("🩺 Agente de Bienestar Preventivo")
st.markdown(
    "Analiza de forma **anónima** los diagnósticos del hospital, diseña campañas de prevención con IA "
    "y, cuando el asegurado cumple su chequeo, **le baja la prima automáticamente** en el CRM."
)
st.info("**Recorrido sugerido:** 1 → analice los diagnósticos · 2 → diseñe y publique las campañas · "
        "3 → procese los chequeos del hospital y vea cómo baja la prima.", icon="👉")

try:
    lista_asegurados = crm.asegurados()
except ErrorCRM as e:
    st.error(f"No se pudo leer el CRM: {e}")
    st.stop()

if not lista_asegurados:
    st.warning("El CRM no tiene asegurados todavía.")
    if st.button("Cargar los 15 asegurados de prueba", type="primary"):
        with st.spinner("Cargando..."):
            crm.reiniciar(asegurados_de_prueba())
        st.rerun()
    st.stop()

paso1, paso2, paso3, tab_crm = st.tabs(["1 · Análisis anónimo", "2 · Campañas", "3 · Chequeos y premios", "CRM: asegurados"])

# --- Paso 1 ---------------------------------------------------------------------

df = analisis.cargar(DATA / "diagnosticos.csv")
tabla = analisis.frecuencias(df)

with paso1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros analizados", f"{len(df):,}")
    c2.metric("Diagnósticos distintos", len(tabla))
    prev = tabla.dropna(subset=["chequeo_preventivo"])
    c3.metric("Casos prevenibles con chequeo", f"{prev['casos'].sum() / len(df) * 100:.0f} %")

    st.subheader("Diagnósticos más frecuentes")
    grafico = tabla.assign(tipo=tabla["chequeo_preventivo"].map(lambda x: "Prevenible con chequeo" if isinstance(x, str) else "Otro"))
    st.bar_chart(grafico, x="diagnostico", y="casos", color="tipo", horizontal=True, sort="-casos", height=380)
    st.dataframe(
        tabla.rename(columns={"codigo_cie10": "CIE-10", "diagnostico": "Diagnóstico", "casos": "Casos",
                              "porcentaje": "%", "chequeo_preventivo": "Chequeo preventivo"}),
        hide_index=True, width="stretch",
    )
    with st.container(border=True):
        st.markdown("🔒 **Privacidad desde el diseño.** Los registros del hospital llegan sin nombre ni póliza. "
                    "Al modelo de IA solo se le envían **conteos agregados**, y los grupos con menos de "
                    f"{analisis.MINIMO_POR_GRUPO} casos se suprimen para que nadie pueda ser identificado.")

# --- Paso 2 ---------------------------------------------------------------------

with paso2:
    top = st.slider("¿Cuántos diagnósticos prevenibles atacar?", 3, 7, 5)
    resumen = analisis.resumen_para_ia(df, top)
    with st.expander("Ver exactamente lo que recibe la IA (datos agregados, sin identidades)"):
        st.json(resumen)

    if st.button("🤖 Diseñar campañas con IA", type="primary"):
        with st.spinner("El agente está diseñando las campañas..."):
            st.session_state.propuestas = campanas.disenar(resumen, groq_key, groq_modelo)

    if "propuestas" in st.session_state:
        propuestas, origen = st.session_state.propuestas
        st.caption("Diseñadas por la IA (Groq) y validadas por reglas clínicas." if origen == "ia"
                   else f"Generadas con {origen}.")
        for c in propuestas:
            with st.container(border=True):
                a, b = st.columns([3, 1])
                a.markdown(f"**{c['nombre']}**  \n{CHEQUEOS[c['tipo_chequeo']]} · motivada por *{c['diagnostico']}*")
                publico = {"M": "Hombres", "F": "Mujeres", "Todos": "Todos"}[c["sexo"]]
                b.markdown(f"**+{c['puntos']} pts**  \n{publico}, {c['edad_min']}-{c['edad_max']} años")
                st.write(f"💬 {c['mensaje']}")
                if c.get("justificacion"):
                    st.caption(f"Por qué: {c['justificacion']}")
        if st.button("📤 Publicar campañas en el CRM"):
            with st.spinner("Publicando en el CRM..."):
                crm.cerrar_campanas_activas()
                for c in propuestas:
                    crm.crear_campana(c)
            del st.session_state.propuestas
            st.success(f"{len(propuestas)} campañas activas en el CRM. Las anteriores quedaron cerradas.")

    activas = crm.campanas(solo_activas=True)
    st.subheader(f"Campañas activas en el CRM ({len(activas)})")
    if activas:
        st.dataframe(pd.DataFrame(activas)[["nombre", "tipo_chequeo", "sexo", "edad_min", "edad_max", "puntos"]],
                     hide_index=True, width="stretch")
    else:
        st.caption("Todavía no hay campañas activas.")

# --- Paso 3 ---------------------------------------------------------------------

with paso3:
    st.subheader("Chequeos reportados por el hospital")
    st.dataframe(pd.DataFrame(st.session_state.feed), hide_index=True, width="stretch")

    with st.form("simular"):
        st.markdown("**Simular un chequeo nuevo** (como si el hospital lo reportara ahora)")
        s1, s2 = st.columns(2)
        opciones = {f"{a['poliza']} · {a['nombre']} ({a['sexo']}, {a['edad']})": a["poliza"] for a in lista_asegurados}
        quien = s1.selectbox("Asegurado", list(opciones))
        tipo = s2.selectbox("Chequeo realizado", list(CHEQUEOS), format_func=lambda t: CHEQUEOS[t])
        if st.form_submit_button("Reportar chequeo"):
            st.session_state.feed.append({
                # ID único: varias personas pueden usar la demo a la vez sobre el mismo CRM.
                "id_chequeo": f"CHQ-{uuid.uuid4().hex[:6].upper()}", "poliza": opciones[quien],
                "tipo_chequeo": tipo, "fecha": pd.Timestamp.today().date().isoformat(),
            })
            st.rerun()

    st.caption("El CRM es compartido: si los chequeos aparecen como «Ya premiado», otra persona ya los "
               "procesó. Use **Reiniciar demostración** en la barra lateral para empezar de cero.")
    if st.button("🏆 Procesar chequeos y premiar", type="primary"):
        with st.spinner("Verificando chequeos y actualizando primas..."):
            st.session_state.decisiones = premios.aplicar(crm, st.session_state.feed)

    if "decisiones" in st.session_state:
        decisiones = st.session_state.decisiones
        premiados = [d for d in decisiones if d.estado == "Premiado"]
        m1, m2, m3 = st.columns(3)
        m1.metric("Premiados ahora", len(premiados))
        m2.metric("Rechazados", sum(d.estado == "Rechazado" for d in decisiones))
        m3.metric("Ahorro mensual otorgado", f"${sum(d.prima_antes - d.prima_despues for d in premiados):.2f}")
        icono = {"Premiado": "✅", "Rechazado": "❌", "Ya premiado": "↩️"}
        st.dataframe(pd.DataFrame([{
            "": icono[d.estado], "Chequeo": d.id_chequeo, "Póliza": d.poliza, "Tipo": d.tipo, "Resultado": d.estado,
            "Detalle": d.motivo + (f" Sube a {d.nivel_nuevo}." if d.subio_de_nivel else ""),
            "Prima": f"${d.prima_antes:.2f} → ${d.prima_despues:.2f}" if d.estado == "Premiado" else "",
        } for d in decisiones]), hide_index=True, width="stretch")
        if any(d.subio_de_nivel for d in premiados):
            st.balloons()

# --- CRM ------------------------------------------------------------------------

with tab_crm:
    tabla_crm = pd.DataFrame(crm.asegurados()).drop(columns=["id"])
    medalla = {"Bronce": "🥉 Bronce", "Plata": "🥈 Plata", "Oro": "🥇 Oro"}
    tabla_crm["nivel"] = tabla_crm["nivel"].map(medalla)
    st.dataframe(
        tabla_crm.rename(columns={"poliza": "Póliza", "nombre": "Nombre", "sexo": "Sexo", "edad": "Edad",
                                  "prima_base": "Prima base", "puntos": "Puntos", "nivel": "Nivel",
                                  "descuento": "Descuento %", "prima_final": "Prima final"}),
        hide_index=True, width="stretch",
        column_config={"Prima base": st.column_config.NumberColumn(format="$%.2f"),
                       "Prima final": st.column_config.NumberColumn(format="$%.2f")},
    )
    st.caption("Niveles: 🥉 Bronce 0-99 pts (0 %) · 🥈 Plata 100-199 pts (5 %) · 🥇 Oro 200+ pts (10 % de descuento en la prima).")
