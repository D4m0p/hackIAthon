"""Panel del Agente de Bienestar Preventivo.  Ejecutar:  streamlit run app.py"""

import os
import time
import uuid
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from agente import analisis, campanas, impacto, perfil, premios, ui
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
        for k in ("feed", "propuestas", "decisiones", "resumen_piloto"):
            st.session_state.pop(k, None)
        st.rerun()
    st.caption("Todos los datos son **ficticios**, generados para esta demostración.")

# --- Encabezado -----------------------------------------------------------------

df = analisis.cargar(DATA / "diagnosticos.csv")
tabla = analisis.frecuencias(df)

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

# --- Piloto automático: el agente completo con un solo botón --------------------

if st.button("▶  Ejecutar el agente completo", key="piloto", width="stretch",
             help="Analiza, diseña las campañas con IA, las publica y premia los chequeos, sin intervención."):
    with st.status("El agente está trabajando de forma autónoma...", expanded=True) as estado:
        resumen_auto = analisis.resumen_para_ia(df, 5)
        st.write(f"🔬 **Analizando** {len(df):,} diagnósticos anónimos del hospital...")
        time.sleep(.5)
        st.write("🎯 Diagnósticos prevenibles más frecuentes: "
                 + ", ".join(r["diagnostico"].lower() for r in resumen_auto) + ".")
        time.sleep(.5)
        st.write("🤖 **Diseñando** una campaña por diagnóstico con IA..." if groq_key
                 else "📄 **Diseñando** campañas con plantillas (sin clave de IA)...")
        nuevas, _ = campanas.disenar(resumen_auto, groq_key, groq_modelo)
        st.write("🩺 Validando cada campaña con reglas clínicas.")
        st.write(f"📤 **Publicando** {len(nuevas)} campañas en el CRM...")
        crm.cerrar_campanas_activas()
        for c in nuevas:
            crm.crear_campana(c)
        st.write(f"🏥 **Verificando** {len(st.session_state.feed)} chequeos reportados por el hospital...")
        decisiones_auto = premios.aplicar(crm, st.session_state.feed)
        premiados_auto = [d for d in decisiones_auto if d.estado == "Premiado"]
        st.write(f"🏆 **Premiando**: {len(premiados_auto)} chequeos cumplidos, primas recalculadas en el CRM.")
        time.sleep(.4)
        estado.update(label="El agente terminó su ciclo completo", state="complete", expanded=False)
    st.session_state.decisiones = decisiones_auto
    st.session_state.globos = any(d.subio_de_nivel for d in premiados_auto)
    st.session_state.resumen_piloto = {
        "campanas": len(nuevas), "premiados": len(premiados_auto),
        "suben": len({d.poliza for d in premiados_auto if d.subio_de_nivel}),
        "ahorro": sum(d.prima_antes - d.prima_despues for d in premiados_auto),
    }
    st.rerun()

if r := st.session_state.get("resumen_piloto"):
    st.markdown(ui.resumen_piloto(r), unsafe_allow_html=True)
    st.caption("Recorra las pestañas para ver el detalle de cada paso.")
    if st.session_state.pop("globos", False):
        st.balloons()

paso1, paso2, paso3, tab_crm, tab_perfil, tab_impacto = st.tabs(
    ["Análisis anónimo", "Campañas", "Chequeos y premios", "Asegurados", "Perfil", "Impacto económico"])

# --- Paso 1 ---------------------------------------------------------------------

with paso1:
    st.markdown(ui.seccion("analisis", "🔬", "Análisis anónimo", "Qué diagnósticos se repiten más entre los asegurados, sin ver a ninguna persona."), unsafe_allow_html=True)
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
                        scale=alt.Scale(domain=["Prevenible con chequeo", "Otro"], range=["#00719B", "#C3D3D8"])),
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

    st.subheader("Mapa de riesgo")
    st.caption("Dónde se concentra cada enfermedad prevenible según sexo y edad. De aquí salen las poblaciones "
               f"objetivo de las campañas. Las celdas con menos de {analisis.MINIMO_POR_GRUPO} casos se ocultan por privacidad.")
    matriz = analisis.matriz_riesgo(df)
    orden_diag = (matriz.groupby("diagnostico")["casos"].sum().sort_values(ascending=False).index.tolist())
    tope = matriz["casos"].max()
    columnas_mapa = st.columns(2, gap="medium")
    for col, sexo in zip(columnas_mapa, ["Mujeres", "Hombres"]):
        datos = matriz[matriz["sexo"] == sexo].assign(valor=lambda d: d["casos"].fillna(0))
        base = alt.Chart(datos).encode(
            x=alt.X("rango_edad:N", title="Edad", sort=analisis.ETIQUETAS, axis=alt.Axis(labelAngle=0, orient="top", labelOverlap=False, labelFontSize=10)),
            y=alt.Y("diagnostico:N", title=None, sort=orden_diag, axis=alt.Axis(labelLimit=220)),
        )
        celdas = base.mark_rect(cornerRadius=7, stroke="#FFFFFF", strokeWidth=3).encode(
            color=alt.condition(
                "datum.suprimido", alt.value("#E4EDEF"),
                alt.Color("valor:Q", legend=None, scale=alt.Scale(
                    domain=[0, tope * .35, tope * .7, tope], range=["#E4EFF4", "#9AC7DA", "#3689AC", "#0C4A64"]))),
            tooltip=[alt.Tooltip("diagnostico", title="Diagnóstico"), alt.Tooltip("rango_edad", title="Edad"),
                     alt.Tooltip("etiqueta", title="Casos")],
        )
        numeros = base.mark_text(fontSize=12, fontWeight=600).encode(
            text="etiqueta:N",
            color=alt.condition(f"datum.valor > {tope * .45}", alt.value("#FFFFFF"), alt.value("#16262C")),
        )
        col.markdown(f"**{sexo}**")
        col.altair_chart((celdas + numeros).properties(height=46 * datos["diagnostico"].nunique() + 40)
                         .configure_view(stroke=None).configure(background="transparent"), width="stretch")

    st.markdown(ui.privacidad(analisis.MINIMO_POR_GRUPO), unsafe_allow_html=True)

# --- Paso 2 ---------------------------------------------------------------------

with paso2:
    st.markdown(ui.seccion("campanas", "📣", "Campañas de prevención", "La IA propone una campaña por cada diagnóstico prevenible y usted las publica en el CRM."), unsafe_allow_html=True)
    top = st.slider("¿Cuántos diagnósticos prevenibles atacar?", 3, 7, 5)
    resumen = analisis.resumen_para_ia(df, top)
    with st.expander("Ver exactamente lo que recibe la IA (datos agregados, sin identidades)"):
        st.json(resumen)

    if st.button("Diseñar campañas con IA", type="primary", icon="✨"):
        with st.status("El agente está diseñando las campañas...", expanded=True) as estado:
            st.write(f"🔒 Leyendo el resumen anónimo: {len(resumen)} diagnósticos prevenibles, sin nombres ni pólizas.")
            time.sleep(.4)
            st.write("🎯 Buscando los grupos de sexo y edad más afectados en cada diagnóstico.")
            time.sleep(.4)
            st.write("🤖 Pidiendo al modelo de IA una campaña por diagnóstico..." if groq_key
                     else "📄 Sin clave de IA: usando campañas de plantilla.")
            resultado = campanas.disenar(resumen, groq_key, groq_modelo)
            st.write("🩺 Validando cada propuesta con reglas clínicas: sexo, rango de edad y puntos.")
            time.sleep(.4)
            st.session_state.propuestas = resultado
            estado.update(label=f"{len(resultado[0])} campañas listas para revisar", state="complete", expanded=False)

    if "propuestas" in st.session_state:
        propuestas, origen = st.session_state.propuestas
        st.caption("Diseñadas por la IA (Groq) y validadas con reglas clínicas." if origen == "ia"
                   else f"Generadas con {origen}.")
        izq, der = st.columns([3, 2], gap="large")
        izq.markdown(ui.campanas(propuestas, CHEQUEOS), unsafe_allow_html=True)
        der.markdown(ui.telefono(propuestas), unsafe_allow_html=True)
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
    st.markdown(ui.seccion("premios", "🏆", "Chequeos y premios", "El hospital reporta los chequeos realizados y el agente premia a quien cumple."), unsafe_allow_html=True)
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
    st.markdown(ui.linea_hospital(st.session_state.feed, lista_asegurados, st.session_state.get("decisiones")),
                unsafe_allow_html=True)

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
        with st.status("El agente está verificando los chequeos...", expanded=True) as estado:
            st.write(f"🏥 Leyendo {len(st.session_state.feed)} chequeos reportados por el hospital.")
            time.sleep(.4)
            st.write("🔗 Cruzando cada póliza con el CRM y con las campañas activas.")
            time.sleep(.4)
            st.write("🧮 Sumando puntos, subiendo niveles y recalculando primas en el CRM.")
            st.session_state.decisiones = premios.aplicar(crm, st.session_state.feed)
            estado.update(label="Chequeos procesados", state="complete", expanded=False)
        st.session_state.globos = any(d.subio_de_nivel for d in st.session_state.decisiones)
        st.rerun()

# --- CRM ------------------------------------------------------------------------

with tab_crm:
    st.markdown(ui.seccion("crm", "🗂️", "CRM de asegurados", "Puntos, nivel y prima de cada asegurado, tal como quedan en Notion."), unsafe_allow_html=True)
    if not any(a["puntos"] for a in lista_asegurados):
        st.info("Todavía nadie ha sumado puntos. Procese los chequeos en la pestaña anterior para ver el podio.", icon="🏁")
    st.markdown(ui.ranking(lista_asegurados), unsafe_allow_html=True)
    st.write("")
    tabla_crm = pd.DataFrame(lista_asegurados).drop(columns=["id"])
    medalla = {"Bronce": "🥉 Bronce", "Plata": "🥈 Plata", "Oro": "🥇 Oro"}
    tabla_crm["nivel"] = tabla_crm["nivel"].map(medalla)
    with st.expander("Ver la tabla completa del CRM"):
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

# --- Perfil del asegurado ----------------------------------------------------------

with tab_perfil:
    st.markdown(ui.seccion("miembro", "💳", "Perfil del asegurado",
                           "Su tarjeta, sus logros y lo que el agente le recomienda hacer a continuación."), unsafe_allow_html=True)
    orden = sorted(lista_asegurados, key=lambda a: (-a["puntos"], a["nombre"]))
    etiquetas = {f"{a['nombre']} · {a['poliza']}": a for a in orden}
    elegido = etiquetas[st.selectbox("Asegurado", list(etiquetas), label_visibility="collapsed")]
    hechos = [h["tipo"] for h in crm.historial() if h["poliza"] == elegido["poliza"]]
    izq, der = st.columns([1.15, 1], gap="large")
    with izq:
        st.markdown(ui.membresia(elegido), unsafe_allow_html=True)
        st.write("")
        st.markdown(ui.anillo(elegido), unsafe_allow_html=True)
    with der:
        st.markdown("**Lo que el agente le recomienda**")
        st.markdown(ui.recomendaciones(perfil.recomendaciones(elegido, activas, hechos)), unsafe_allow_html=True)
    st.markdown("**Insignias**")
    st.markdown(ui.insignias(perfil.insignias(elegido, hechos)), unsafe_allow_html=True)

# --- Impacto económico ---------------------------------------------------------------

with tab_impacto:
    st.markdown(ui.seccion("economia", "📈", "Impacto económico",
                           "Por qué a la aseguradora le conviene pagar por la prevención."), unsafe_allow_html=True)
    base_campanas = activas or campanas.disenar(analisis.resumen_para_ia(df, 5), None)[0]
    c1, c2 = st.columns(2)
    n_asegurados = c1.slider("Asegurados en la cartera", 1_000, 100_000, 10_000, step=1_000, format="%d")
    participacion = c2.slider("Participación en las campañas", 10, 80, 30, format="%d %%") / 100
    with st.expander("Supuestos por chequeo (cifras referenciales, puede editarlas)"):
        supuestos = st.data_editor(
            impacto.supuestos_tabla(sorted({c["tipo_chequeo"] for c in base_campanas})),
            hide_index=True, width="stretch", disabled=["tipo", "Chequeo"], column_config={"tipo": None})
    prima_prom = sum(a["prima_base"] for a in lista_asegurados) / len(lista_asegurados)
    res = impacto.calcular(df, base_campanas, supuestos, n_asegurados, participacion, prima_prom, descuento_promedio=5)
    st.markdown(ui.impacto(res, n_asegurados, participacion), unsafe_allow_html=True)
    if not res["detalle"].empty:
        largo = res["detalle"].melt(id_vars=["Campaña"], value_vars=["Ahorro en tratamientos", "Costo de los chequeos"],
                                    var_name="Concepto", value_name="USD")
        st.altair_chart(alt.Chart(largo).mark_bar(cornerRadiusEnd=5, height=14).encode(
            x=alt.X("USD:Q", title="USD por año", axis=alt.Axis(format="$,.0f")),
            y=alt.Y("Campaña:N", title=None, axis=alt.Axis(labelLimit=260)),
            yOffset="Concepto:N",
            color=alt.Color("Concepto:N", title=None, legend=alt.Legend(orient="top"),
                            scale=alt.Scale(range=["#00719B", "#C3D3D8"])),
            tooltip=["Campaña", "Concepto", alt.Tooltip("USD:Q", format="$,.0f")],
        ).properties(height=320), width="stretch")
    st.caption("Estimación ilustrativa para la demostración: los costos y tasas de hallazgo son referenciales y se pueden "
               "ajustar en los supuestos. La población objetivo sale de la distribución de edad y sexo del hospital. "
               f"Descuento promedio considerado: 5 % sobre una prima de ${prima_prom:.2f} al mes.")
