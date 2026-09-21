"""Panel del Agente de Bienestar Preventivo.  Ejecutar:  streamlit run app.py"""

import os
import uuid
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from agente import analisis, campanas, premios, ui
from agente.catalogo import CHEQUEOS
from agente.crm import CRM, CRMLocal, ErrorCRM

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Agente de Bienestar Preventivo", page_icon="🩺", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)


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

try:
    lista_asegurados = crm.asegurados()
    activas = crm.campanas(solo_activas=True)
except ErrorCRM as e:
    st.error(f"No se pudo leer el CRM: {e}")
    st.stop()

con_descuento = [a for a in lista_asegurados if a["descuento"] > 0]
ahorro_total = sum(a["prima_base"] - a["prima_final"] for a in con_descuento)
st.markdown(ui.hero(len(activas), len(con_descuento), ahorro_total), unsafe_allow_html=True)
st.write("")

if not lista_asegurados:
    st.warning("El CRM no tiene asegurados todavía.")
    if st.button("Cargar los 15 asegurados de prueba", type="primary"):
        with st.spinner("Cargando..."):
            crm.reiniciar(asegurados_de_prueba())
        st.rerun()
    st.stop()

if aviso := st.session_state.pop("aviso", None):
    st.toast(aviso, icon="✅")

paso1, paso2, paso3, tab_crm = st.tabs(["Análisis anónimo", "Campañas", "Chequeos y premios", "CRM de asegurados"])

# --- Paso 1 ---------------------------------------------------------------------

df = analisis.cargar(DATA / "diagnosticos.csv")
tabla = analisis.frecuencias(df)

with paso1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Registros analizados", f"{len(df):,}")
    c2.metric("Diagnósticos distintos", len(tabla))
    prev = tabla.dropna(subset=["chequeo_preventivo"])
    c3.metric("Casos prevenibles con un chequeo", f"{prev['casos'].sum() / len(df) * 100:.0f} %")

    st.subheader("Diagnósticos más frecuentes")
    grafico = tabla.assign(tipo=tabla["chequeo_preventivo"].map(lambda x: "Prevenible con chequeo" if isinstance(x, str) else "Otro"))
    barras = alt.Chart(grafico).mark_bar(cornerRadiusEnd=6, height=22).encode(
        x=alt.X("casos:Q", title="Casos"),
        y=alt.Y("diagnostico:N", sort="-x", title=None, axis=alt.Axis(labelLimit=320, labelFontSize=13)),
        color=alt.Color("tipo:N", title=None, legend=alt.Legend(orient="top"),
                        scale=alt.Scale(domain=["Prevenible con chequeo", "Otro"], range=["#0FB5C4", "#B7CBD3"])),
        tooltip=[alt.Tooltip("diagnostico", title="Diagnóstico"), alt.Tooltip("casos", title="Casos"),
                 alt.Tooltip("porcentaje", title="% del total")],
    ).properties(height=400)
    st.altair_chart(barras, width="stretch")
    with st.expander("Ver la tabla completa"):
        st.dataframe(
            tabla.rename(columns={"codigo_cie10": "CIE-10", "diagnostico": "Diagnóstico", "casos": "Casos",
                                  "porcentaje": "%", "chequeo_preventivo": "Chequeo preventivo"}),
            hide_index=True, width="stretch",
        )
    st.markdown(ui.privacidad(analisis.MINIMO_POR_GRUPO), unsafe_allow_html=True)

# --- Paso 2 ---------------------------------------------------------------------

with paso2:
    top = st.slider("¿Cuántos diagnósticos prevenibles atacar?", 3, 7, 5)
    resumen = analisis.resumen_para_ia(df, top)
    with st.expander("Ver exactamente lo que recibe la IA (datos agregados, sin identidades)"):
        st.json(resumen)

    if st.button("Diseñar campañas con IA", type="primary", icon="✨"):
        with st.spinner("El agente está diseñando las campañas..."):
            st.session_state.propuestas = campanas.disenar(resumen, groq_key, groq_modelo)

    if "propuestas" in st.session_state:
        propuestas, origen = st.session_state.propuestas
        st.caption("Diseñadas por la IA (Groq) y validadas con reglas clínicas." if origen == "ia"
                   else f"Generadas con {origen}.")
        st.markdown(ui.campanas(propuestas, CHEQUEOS), unsafe_allow_html=True)
        if st.button("Publicar campañas en el CRM", type="primary", icon="📤"):
            with st.spinner("Publicando en el CRM..."):
                crm.cerrar_campanas_activas()
                for c in propuestas:
                    crm.crear_campana(c)
            del st.session_state.propuestas
            st.session_state.aviso = f"{len(propuestas)} campañas publicadas. Las anteriores quedaron cerradas."
            st.rerun()

    st.subheader(f"Campañas activas en el CRM ({len(activas)})")
    if activas:
        st.markdown(ui.campanas(activas, CHEQUEOS), unsafe_allow_html=True)
    else:
        st.caption("Todavía no hay campañas activas. Diséñelas con el botón de arriba y publíquelas.")

# --- Paso 3 ---------------------------------------------------------------------

with paso3:
    if "decisiones" in st.session_state:
        decisiones = st.session_state.decisiones
        premiados = [d for d in decisiones if d.estado == "Premiado"]
        otros = [d for d in decisiones if d.estado != "Premiado"]
        if premiados:
            st.subheader(f"Premiados: {len(premiados)}")
            st.markdown(ui.carnets(premiados), unsafe_allow_html=True)
        else:
            st.info("Ningún chequeo nuevo para premiar.")
        if otros:
            st.subheader(f"No premiados: {len(otros)}")
            st.markdown(ui.rechazos(otros), unsafe_allow_html=True)
        if st.session_state.pop("globos", False):
            st.balloons()
        st.divider()

    st.subheader("Chequeos reportados por el hospital")
    st.dataframe(pd.DataFrame(st.session_state.feed).rename(columns={
        "id_chequeo": "Chequeo", "poliza": "Póliza", "tipo_chequeo": "Tipo", "fecha": "Fecha"}),
        hide_index=True, width="stretch")

    with st.form("simular"):
        st.markdown("**Simular un chequeo nuevo**, como si el hospital lo reportara ahora")
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
    if st.button("Procesar chequeos y premiar", type="primary", icon="🏆"):
        with st.spinner("Verificando chequeos y actualizando primas..."):
            st.session_state.decisiones = premios.aplicar(crm, st.session_state.feed)
        st.session_state.globos = any(d.subio_de_nivel for d in st.session_state.decisiones)
        st.rerun()

# --- CRM ------------------------------------------------------------------------

with tab_crm:
    tabla_crm = pd.DataFrame(lista_asegurados).drop(columns=["id"])
    medalla = {"Bronce": "🥉 Bronce", "Plata": "🥈 Plata", "Oro": "🥇 Oro"}
    tabla_crm["nivel"] = tabla_crm["nivel"].map(medalla)
    st.dataframe(
        tabla_crm.rename(columns={"poliza": "Póliza", "nombre": "Nombre", "sexo": "Sexo", "edad": "Edad",
                                  "prima_base": "Prima base", "puntos": "Puntos", "nivel": "Nivel",
                                  "descuento": "Descuento %", "prima_final": "Prima final"}),
        hide_index=True, width="stretch", height=565,
        column_config={"Prima base": st.column_config.NumberColumn(format="$%.2f"),
                       "Prima final": st.column_config.NumberColumn(format="$%.2f"),
                       "Puntos": st.column_config.ProgressColumn(min_value=0, max_value=300, format="%d")},
    )
    st.caption("Niveles: 🥉 Bronce de 0 a 99 puntos, sin descuento. 🥈 Plata de 100 a 199 puntos, 5 % de descuento. "
               "🥇 Oro desde 200 puntos, 10 % de descuento en la prima.")
