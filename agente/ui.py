"""Capa visual del panel: estilos y piezas HTML. No contiene lógica del agente."""

from html import escape

from agente.catalogo import CHEQUEOS

GRADIENTE = "linear-gradient(125deg, #0FB5C4 0%, #2F6BFF 55%, #7B5CFF 100%)"

CSS = f"""
<style>
/* Fondo tipo aurora: manchas de color muy suaves y fijas */
.stApp {{
  background:
    radial-gradient(40rem 28rem at 8% -6%, rgba(15,181,196,.20), transparent 70%),
    radial-gradient(36rem 26rem at 96% 4%, rgba(123,92,255,.16), transparent 70%),
    radial-gradient(44rem 30rem at 60% 110%, rgba(47,107,255,.10), transparent 70%),
    #F3FAFB;
  background-attachment: fixed;
}}
.block-container {{ padding-top: 4.2rem; max-width: 1200px; }}

/* Encabezado protagonista */
.hero {{
  position: relative; overflow: hidden; border-radius: 1.6rem; padding: 2.1rem 2.2rem 1.6rem;
  color: #fff; background: {GRADIENTE}; background-size: 180% 180%;
  animation: aurora 14s ease-in-out infinite alternate;
  box-shadow: 0 18px 50px -18px rgba(47,107,255,.55);
}}
.hero::after {{
  content: ""; position: absolute; inset: -40% -10% auto auto; width: 32rem; height: 32rem;
  background: radial-gradient(circle, rgba(94,230,224,.55), transparent 62%); pointer-events: none;
}}
@keyframes aurora {{ from {{ background-position: 0% 40%; }} to {{ background-position: 100% 60%; }} }}
@media (prefers-reduced-motion: reduce) {{ .hero {{ animation: none; }} }}
.hero h1 {{
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: clamp(2rem, 4vw, 3.1rem);
  line-height: 1.02; letter-spacing: -.02em; margin: 0 0 .6rem; color: #fff; padding: 0;
}}
.hero p {{ max-width: 44rem; font-size: 1.05rem; line-height: 1.5; opacity: .93; margin: 0; }}
.pasos {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: .8rem; margin-top: 1.6rem; position: relative; z-index: 1; }}
.paso {{
  border-radius: 1rem; padding: .85rem 1rem; background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.28); backdrop-filter: blur(6px);
}}
.paso.hecho {{ background: rgba(255,255,255,.26); border-color: rgba(255,255,255,.6); }}
.paso b {{ display: block; font-size: 1rem; }}
.paso span {{ font-size: .88rem; opacity: .9; }}
.paso .num {{
  display: inline-grid; place-items: center; width: 1.6rem; height: 1.6rem; border-radius: 50%;
  margin-right: .45rem; font-weight: 700; font-size: .85rem; background: rgba(255,255,255,.25);
}}
.paso.hecho .num {{ background: #fff; color: #2F6BFF; }}
@media (max-width: 720px) {{ .pasos {{ grid-template-columns: 1fr; }} .hero {{ padding: 1.5rem 1.2rem; }} }}

/* Pestañas en forma de píldora */
.stTabs [role="tablist"] {{
  gap: .3rem; background: rgba(255,255,255,.75); padding: .35rem; border-radius: 999px;
  width: fit-content; max-width: 100%; border: 1px solid #D5ECEF; box-shadow: none;
}}
.stTabs [data-testid="stTab"] {{ border-radius: 999px; padding: .5rem 1.15rem; height: auto; transition: background .2s; }}
.stTabs [data-testid="stTab"]:hover {{ background: rgba(15,181,196,.10); }}
.stTabs [data-testid="stTab"][aria-selected="true"] {{ background: {GRADIENTE}; }}
.stTabs [data-testid="stTab"][aria-selected="true"] p {{ color: #fff; font-weight: 600; }}
.stTabs .react-aria-SelectionIndicator {{ display: none; }}
.stTabs [data-testid="stTab"]:focus-visible {{ outline: 3px solid #7B5CFF; outline-offset: 2px; }}

/* Transición al cambiar de sección: Streamlit monta el panel de nuevo en cada cambio */
.stTabs [data-testid="stTab"] {{
  transition: background .35s ease, box-shadow .35s ease, transform .25s ease;
}}
.stTabs [data-testid="stTab"][aria-selected="true"] {{
  box-shadow: 0 6px 18px -6px rgba(47,107,255,.65), 0 0 0 3px rgba(15,181,196,.14);
  transform: translateY(-1px);
}}
.stTabs [role="tabpanel"] {{ animation: entrar .6s cubic-bezier(.22,1,.36,1) both; }}
@keyframes entrar {{
  from {{ opacity: 0; transform: translateY(18px); filter: blur(6px); }}
  to   {{ opacity: 1; transform: none; filter: none; }}
}}
.grilla > *, [data-testid="stMetric"] {{ animation: entrar .7s cubic-bezier(.22,1,.36,1) both; }}
.grilla > :nth-child(2) {{ animation-delay: .07s; }}
.grilla > :nth-child(3) {{ animation-delay: .14s; }}
.grilla > :nth-child(4) {{ animation-delay: .21s; }}
.grilla > :nth-child(5) {{ animation-delay: .28s; }}
.grilla > :nth-child(n+6) {{ animation-delay: .35s; }}
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {{ animation-delay: .08s; }}
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {{ animation-delay: .16s; }}

/* Encabezado de cada sección, con su propio degradado */
.seccion {{
  display: flex; align-items: center; gap: 1rem; margin: .6rem 0 1.3rem; padding: 1rem 1.2rem;
  border-radius: 1.2rem; background: rgba(255,255,255,.8); border: 1px solid #D5ECEF; position: relative; overflow: hidden;
}}
.seccion::after {{
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(100deg, transparent 30%, rgba(255,255,255,.55) 50%, transparent 70%);
  transform: translateX(-100%); animation: brillo 1.1s .25s ease-out both;
}}
@keyframes brillo {{ to {{ transform: translateX(100%); }} }}
.seccion .icono {{
  flex: none; display: grid; place-items: center; width: 3.1rem; height: 3.1rem; border-radius: 1rem;
  font-size: 1.5rem; box-shadow: 0 10px 22px -10px rgba(47,107,255,.7);
  animation: aparecer .7s cubic-bezier(.34,1.56,.64,1) both;
}}
@keyframes aparecer {{ from {{ transform: scale(.4) rotate(-12deg); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
.seccion h3 {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.35rem; margin: 0; padding: 0; line-height: 1.15; }}
.seccion p {{ margin: .15rem 0 0; color: #466373; font-size: .95rem; }}
.seccion.analisis .icono {{ background: linear-gradient(135deg, #5EE6E0, #0FB5C4); }}
.seccion.campanas .icono {{ background: linear-gradient(135deg, #0FB5C4, #2F6BFF); }}
.seccion.premios  .icono {{ background: linear-gradient(135deg, #2F6BFF, #7B5CFF); }}
.seccion.crm      .icono {{ background: linear-gradient(135deg, #7B5CFF, #0FB5C4); }}
.seccion.analisis {{ border-left: 5px solid #0FB5C4; }}
.seccion.campanas {{ border-left: 5px solid #2F6BFF; }}
.seccion.premios  {{ border-left: 5px solid #7B5CFF; }}
.seccion.crm      {{ border-left: 5px solid #5E8BFF; }}

@media (prefers-reduced-motion: reduce) {{
  .stTabs [role="tabpanel"], .grilla > *, [data-testid="stMetric"], .seccion .icono {{ animation: none; }}
  .seccion::after {{ display: none; }}
}}

/* Métricas como tarjetas translúcidas */
[data-testid="stMetric"] {{
  background: rgba(255,255,255,.8); border: 1px solid #D5ECEF; border-radius: 1.1rem; padding: 1rem 1.2rem;
}}
[data-testid="stMetricValue"] {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; color: #0B6E78; }}

/* Botón principal con degradado */
.stButton button[kind="primary"], .stFormSubmitButton button {{
  background: {GRADIENTE}; border: 0; color: #fff; font-weight: 600;
  box-shadow: 0 8px 22px -10px rgba(47,107,255,.7);
}}
.stButton button[kind="primary"]:hover, .stFormSubmitButton button:hover {{ filter: brightness(1.07); color: #fff; }}
button:focus-visible {{ outline: 3px solid #7B5CFF !important; outline-offset: 2px; }}

/* Fichas de campaña */
.grilla {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1rem; margin: .6rem 0 1rem; }}
.campana {{
  position: relative; border-radius: 1.2rem; padding: 1.2rem 1.2rem 1.05rem; background: rgba(255,255,255,.86);
  border: 1px solid #D5ECEF; overflow: hidden;
}}
.campana::before {{ content: ""; position: absolute; inset: 0 0 auto 0; height: 5px; background: {GRADIENTE}; }}
.campana .fila {{ display: flex; justify-content: space-between; align-items: flex-start; gap: .8rem; }}
.campana h4 {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.12rem; margin: .1rem 0 .2rem; padding: 0; line-height: 1.2; }}
.campana .chequeo {{ color: #466373; font-size: .9rem; }}
.pts {{
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.7rem; line-height: 1; white-space: nowrap;
  background: {GRADIENTE}; -webkit-background-clip: text; background-clip: text; color: transparent;
}}
.pts small {{ font-size: .8rem; font-weight: 600; }}
.publico {{
  display: inline-block; margin: .7rem 0 .55rem; padding: .22rem .7rem; border-radius: 999px; font-size: .84rem;
  font-weight: 600; color: #0B6E78; background: rgba(15,181,196,.13);
}}
.campana .mensaje {{ font-size: .95rem; line-height: 1.5; margin: 0; }}
.campana .porque {{ font-size: .82rem; color: #5B7784; margin-top: .55rem; }}

/* Carnet del asegurado premiado: el elemento protagonista */
.carnet {{
  position: relative; border-radius: 1.3rem; padding: 1.2rem 1.3rem; color: #fff; overflow: hidden;
  background: {GRADIENTE}; box-shadow: 0 16px 36px -18px rgba(47,107,255,.75);
}}
.carnet::after {{
  content: ""; position: absolute; right: -4rem; bottom: -5rem; width: 14rem; height: 14rem; border-radius: 50%;
  background: radial-gradient(circle, rgba(94,230,224,.5), transparent 65%);
}}
.carnet .cab {{ display: flex; justify-content: space-between; align-items: center; gap: .6rem; }}
.carnet .nombre {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.2rem; }}
.carnet .poliza {{ font-size: .82rem; opacity: .85; }}
.medalla {{ padding: .2rem .65rem; border-radius: 999px; font-size: .8rem; font-weight: 700; color: #0B2533; }}
.medalla.Oro {{ background: #F2B233; }}
.medalla.Plata {{ background: #DDE6EC; }}
.medalla.Bronce {{ background: #E0A477; }}
.carnet .motivo {{ font-size: .88rem; opacity: .92; margin: .6rem 0 .8rem; position: relative; z-index: 1; }}
.carnet .prima {{ display: flex; align-items: baseline; gap: .7rem; position: relative; z-index: 1; }}
.carnet .antes {{ text-decoration: line-through; opacity: .75; font-size: 1rem; }}
.carnet .despues {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 2.1rem; line-height: 1; }}
.carnet .despues small {{ font-size: .85rem; font-weight: 600; opacity: .85; }}
.carnet .sube {{ margin-top: .6rem; font-size: .84rem; font-weight: 600; position: relative; z-index: 1; }}

/* Rechazos: discretos */
.rechazos {{ border-radius: 1rem; background: rgba(255,255,255,.8); border: 1px solid #F1D3D4; padding: .4rem 1rem; }}
.rechazo {{ display: flex; gap: .8rem; padding: .55rem 0; border-bottom: 1px solid #F5E4E5; font-size: .92rem; }}
.rechazo:last-child {{ border-bottom: 0; }}
.rechazo .x {{ color: #E5484D; font-weight: 700; }}
.rechazo .id {{ color: #5B7784; min-width: 7.5rem; }}

/* Nota de privacidad */
.privacidad {{
  border-radius: 1rem; padding: 1rem 1.2rem; margin-top: 1rem; background: rgba(255,255,255,.8);
  border: 1px solid #D5ECEF; border-left: 5px solid #0FB5C4; font-size: .95rem; line-height: 1.5;
}}
</style>
"""

PUBLICO = {"M": "Hombres", "F": "Mujeres", "Todos": "Hombres y mujeres"}


def hero(campanas_activas: int, premios: int, ahorro: float) -> str:
    pasos = [
        ("Analizar", "Diagnósticos del hospital, sin identidades", True),
        ("Diseñar campañas", f"{campanas_activas} campañas activas" if campanas_activas else "Pendiente", campanas_activas > 0),
        ("Premiar chequeos", f"{premios} premiados · ${ahorro:.2f} menos al mes" if premios else "Pendiente", premios > 0),
    ]
    html = "".join(
        f'<div class="paso{" hecho" if hecho else ""}"><b><span class="num">{"✓" if hecho else i}</span>{t}</b>'
        f"<span>{d}</span></div>"
        for i, (t, d, hecho) in enumerate(pasos, 1)
    )
    return (
        '<div class="hero"><h1>Agente de Bienestar Preventivo</h1>'
        "<p>Detecta qué enfermedades son más frecuentes entre los asegurados, lanza campañas de prevención "
        "y, cuando la persona se hace su chequeo, le baja la prima automáticamente en el CRM.</p>"
        f'<div class="pasos">{html}</div></div>'
    )


def campanas(lista: list[dict], nombres_chequeo: dict) -> str:
    fichas = []
    for c in lista:
        porque = f'<div class="porque">Por qué: {escape(c["justificacion"])}</div>' if c.get("justificacion") else ""
        fichas.append(
            '<div class="campana"><div class="fila"><div>'
            f'<h4>{escape(c["nombre"])}</h4><div class="chequeo">{escape(nombres_chequeo[c["tipo_chequeo"]])}</div></div>'
            f'<div class="pts">+{c["puntos"]}<small> pts</small></div></div>'
            f'<span class="publico">{PUBLICO[c["sexo"]]} de {c["edad_min"]} a {c["edad_max"]} años</span>'
            f'<p class="mensaje">{escape(c["mensaje"])}</p>{porque}</div>'
        )
    return f'<div class="grilla">{"".join(fichas)}</div>'


def carnets(premiados: list) -> str:
    tarjetas = []
    for d in premiados:
        a = d.asegurado
        sube = f'<div class="sube">▲ Sube a nivel {d.nivel_nuevo}</div>' if d.subio_de_nivel else ""
        tarjetas.append(
            '<div class="carnet"><div class="cab"><div>'
            f'<div class="nombre">{escape(a["nombre"])}</div><div class="poliza">{escape(d.poliza)} · {escape(CHEQUEOS.get(d.tipo, d.tipo))}</div></div>'
            f'<span class="medalla {d.nivel_nuevo}">{d.nivel_nuevo}</span></div>'
            f'<div class="motivo">{escape(d.motivo)}</div>'
            f'<div class="prima"><span class="antes">${d.prima_antes:.2f}</span>'
            f'<span class="despues">${d.prima_despues:.2f}<small> /mes</small></span></div>{sube}</div>'
        )
    return f'<div class="grilla">{"".join(tarjetas)}</div>'


def rechazos(lista: list) -> str:
    filas = "".join(
        f'<div class="rechazo"><span class="x">{"✕" if d.estado == "Rechazado" else "↺"}</span>'
        f'<span class="id">{escape(d.id_chequeo)}<br>{escape(d.poliza)}</span><span>{escape(d.motivo)}</span></div>'
        for d in lista
    )
    return f'<div class="rechazos">{filas}</div>'


def seccion(clase: str, icono: str, titulo: str, texto: str) -> str:
    return (f'<div class="seccion {clase}"><div class="icono">{icono}</div>'
            f"<div><h3>{titulo}</h3><p>{texto}</p></div></div>")


def privacidad(minimo: int) -> str:
    return (
        '<div class="privacidad">🔒 <b>Privacidad desde el diseño.</b> Los registros del hospital llegan sin nombre '
        "ni póliza. Al modelo de IA solo se le envían conteos agregados, y los grupos con menos de "
        f"{minimo} casos se ocultan para que nadie pueda ser identificado.</div>"
    )
