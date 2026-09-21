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
.carnet .prima {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: .3rem .7rem; position: relative; z-index: 1; }}
.carnet .antes {{ text-decoration: line-through; opacity: .75; font-size: 1rem; }}
.carnet .despues {{ white-space: nowrap; font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 2.1rem; line-height: 1; }}
.carnet .despues small {{ font-size: .85rem; font-weight: 600; opacity: .85; }}
.carnet .sube {{ margin-top: .6rem; font-size: .84rem; font-weight: 600; position: relative; z-index: 1; }}

/* Rechazos: discretos */
.rechazos {{ border-radius: 1rem; background: rgba(255,255,255,.8); border: 1px solid #F1D3D4; padding: .4rem 1rem; }}
.rechazo {{ display: flex; gap: .8rem; padding: .55rem 0; border-bottom: 1px solid #F5E4E5; font-size: .92rem; }}
.rechazo:last-child {{ border-bottom: 0; }}
.rechazo .x {{ color: #E5484D; font-weight: 700; }}
.rechazo .id {{ color: #5B7784; min-width: 7.5rem; }}

/* Prima que baja en vivo: se anima un entero (centavos) y se muestra con contadores CSS */
@property --c {{ syntax: '<integer>'; inherits: false; initial-value: 0; }}
@property --d {{ syntax: '<integer>'; inherits: false; initial-value: 0; }}
.contador {{
  --c: var(--hasta); --d: calc((var(--c) - 50) / 100);
  counter-reset: dol var(--d) cen calc(var(--c) - var(--d) * 100);
  animation: bajar 1.8s .45s cubic-bezier(.16,1,.3,1) both;
}}
.contador::before {{ content: "$" counter(dol) "." counter(cen, decimal-leading-zero); }}
@keyframes bajar {{ from {{ --c: var(--desde); }} to {{ --c: var(--hasta); }} }}
.carnet .antes {{ animation: tachar .5s .3s ease-out both; }}
@keyframes tachar {{ from {{ text-decoration-color: transparent; opacity: 1; }} to {{ text-decoration-color: currentColor; opacity: .75; }} }}
.carnet .ahorro {{
  display: inline-block; margin-left: auto; padding: .15rem .55rem; border-radius: 999px; font-size: .78rem; font-weight: 700; white-space: nowrap;
  background: rgba(255,255,255,.22); animation: entrar .6s 1.9s cubic-bezier(.22,1,.36,1) both;
}}

/* Ranking de asegurados */
.podio {{ display: grid; grid-template-columns: 1fr 1.15fr 1fr; align-items: end; gap: .9rem; margin: .4rem 0 1.4rem; }}
.puesto {{
  text-align: center; border-radius: 1.3rem 1.3rem .8rem .8rem; padding: 1.1rem .8rem 1rem; color: #fff; position: relative;
  box-shadow: 0 16px 34px -18px rgba(47,107,255,.7); animation: subir .8s cubic-bezier(.34,1.4,.64,1) both;
}}
.puesto.p1 {{ background: linear-gradient(160deg, #F2B233, #E58A1F); min-height: 13.5rem; animation-delay: .25s; }}
.puesto.p2 {{ background: linear-gradient(160deg, #0FB5C4, #2F6BFF); min-height: 11.5rem; animation-delay: .1s; }}
.puesto.p3 {{ background: linear-gradient(160deg, #7B5CFF, #2F6BFF); min-height: 10rem; animation-delay: .4s; }}
@keyframes subir {{ from {{ transform: translateY(40px) scale(.96); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
.puesto .lugar {{ font-size: 2.1rem; line-height: 1; }}
.puesto .quien {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.1rem; margin-top: .4rem; }}
.puesto .dato {{ font-size: .85rem; opacity: .92; }}
.puesto .puntaje {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.9rem; margin-top: .3rem; }}
.ranking {{ border-radius: 1.2rem; background: rgba(255,255,255,.85); border: 1px solid #D5ECEF; padding: .3rem 1.1rem; }}
.fila-r {{ display: grid; grid-template-columns: 2rem 1fr 11rem 6.5rem; align-items: center; gap: .9rem; padding: .7rem 0; border-bottom: 1px solid #E4F1F3; }}
.fila-r:last-child {{ border-bottom: 0; }}
.fila-r .pos {{ font-weight: 700; color: #7C98A4; text-align: center; }}
.fila-r .nom b {{ display: block; }}
.fila-r .nom span {{ font-size: .82rem; color: #5B7784; }}
.barra {{ height: .55rem; border-radius: 999px; background: #E1EEF1; overflow: hidden; }}
.barra i {{ display: block; height: 100%; border-radius: inherit; background: {GRADIENTE}; transform-origin: left;
  animation: llenar 1s .3s cubic-bezier(.22,1,.36,1) both; }}
@keyframes llenar {{ from {{ transform: scaleX(0); }} }}
.meta {{ font-size: .78rem; color: #5B7784; margin-top: .25rem; }}
.fila-r .prima {{ text-align: right; font-weight: 700; }}
.fila-r .prima s {{ display: block; font-weight: 400; font-size: .8rem; color: #8AA2AD; }}
@media (max-width: 720px) {{
  .podio {{ gap: .5rem; }} .puesto {{ padding: .8rem .4rem; }} .puesto .quien {{ font-size: .92rem; }}
  .fila-r {{ grid-template-columns: 1.4rem 1fr 5.5rem; }} .fila-r .avance {{ display: none; }}
}}

/* Vista previa en el celular */
.telefono {{
  margin: .6rem auto 0; max-width: 330px; border-radius: 2.6rem; padding: .8rem; background: #0B2533;
  box-shadow: 0 30px 60px -25px rgba(11,37,51,.6), inset 0 0 0 2px #24475a; position: sticky; top: 4.5rem;
}}
.pantalla {{
  border-radius: 2rem; min-height: 34rem; padding: 2.6rem .75rem 1rem; position: relative; overflow: hidden;
  background: linear-gradient(170deg, #0FB5C4 0%, #2F6BFF 55%, #7B5CFF 100%);
}}
.pantalla::before {{ content: ""; position: absolute; top: .6rem; left: 50%; width: 5.5rem; height: 1.4rem; border-radius: 1rem;
  background: #0B2533; transform: translateX(-50%); }}
.pantalla .hora {{ text-align: center; color: #fff; font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 2.6rem; line-height: 1; }}
.pantalla .fecha {{ text-align: center; color: rgba(255,255,255,.85); font-size: .85rem; margin: .2rem 0 1.1rem; }}
.notif {{
  background: rgba(255,255,255,.9); backdrop-filter: blur(10px); border-radius: 1.1rem; padding: .65rem .75rem; margin-bottom: .55rem;
  animation: notificar .6s cubic-bezier(.34,1.4,.64,1) both;
}}
.notif:nth-child(2) {{ animation-delay: .35s; }} .notif:nth-child(3) {{ animation-delay: .7s; }}
.notif:nth-child(4) {{ animation-delay: 1.05s; }} .notif:nth-child(n+5) {{ animation-delay: 1.4s; }}
@keyframes notificar {{ from {{ transform: translateY(-16px) scale(.94); opacity: 0; }} to {{ transform: none; opacity: 1; }} }}
.notif .app {{ display: flex; align-items: center; gap: .4rem; font-size: .72rem; color: #5B7784; }}
.notif .app i {{ width: 1.1rem; height: 1.1rem; border-radius: .35rem; background: {GRADIENTE}; display: inline-block; }}
.notif .app em {{ margin-left: auto; font-style: normal; }}
.notif b {{ display: block; font-size: .86rem; margin: .2rem 0 .1rem; color: #0B2533; }}
.notif p {{ margin: 0; font-size: .8rem; line-height: 1.35; color: #29485A; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}

/* Hospital en vivo: línea de tiempo */
.linea {{ position: relative; margin: .4rem 0 1rem; padding: .2rem .4rem .2rem 1.6rem; max-height: 27rem; overflow-y: auto; }}
.linea::before {{ content: ""; position: absolute; left: .55rem; top: .4rem; bottom: .4rem; width: 3px; border-radius: 3px; background: linear-gradient(#0FB5C4, #7B5CFF); }}
.evento {{
  position: relative; display: grid; grid-template-columns: 2.6rem 1fr auto; gap: .8rem; align-items: center;
  background: rgba(255,255,255,.88); border: 1px solid #D5ECEF; border-radius: 1rem; padding: .65rem .9rem; margin-bottom: .6rem;
  animation: entrar .5s cubic-bezier(.22,1,.36,1) both;
}}
.evento::before {{ content: ""; position: absolute; left: -1.33rem; top: 50%; width: .8rem; height: .8rem; border-radius: 50%;
  transform: translateY(-50%); background: #fff; border: 3px solid #0FB5C4; }}
.evento .ico {{ display: grid; place-items: center; width: 2.6rem; height: 2.6rem; border-radius: .8rem; font-size: 1.3rem; background: rgba(15,181,196,.12); }}
.evento b {{ display: block; font-size: .95rem; }}
.evento span {{ font-size: .82rem; color: #5B7784; }}
.estado {{ padding: .2rem .65rem; border-radius: 999px; font-size: .76rem; font-weight: 700; white-space: nowrap; }}
.estado.nuevo {{ background: rgba(47,107,255,.12); color: #2F6BFF; }}
.estado.premiado {{ background: rgba(16,185,129,.14); color: #0B7A57; }}
.estado.rechazado {{ background: rgba(229,72,77,.12); color: #C0353A; }}
.estado.repetido {{ background: #EEF3F5; color: #5B7784; }}

@media (prefers-reduced-motion: reduce) {{
  .contador, .carnet .antes, .carnet .ahorro, .puesto, .barra i, .notif, .evento {{ animation: none; }}
}}

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


def _etiqueta_ahorro(d) -> str:
    """Ahorro logrado, o cuánto falta para el siguiente nivel si el premio aún no baja la prima."""
    from agente.gamificacion import siguiente_nivel

    ahorro = d.prima_antes - d.prima_despues
    if ahorro > 0:
        return f"−${ahorro:.2f} al mes"
    sig = siguiente_nivel(d.asegurado["puntos"] + d.puntos)
    return f"Le faltan {sig[1]} pts para {sig[0]}" if sig else "Nivel máximo"


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
            f'<span class="despues"><span class="contador" role="img" aria-label="${d.prima_despues:.2f}" '
            f'style="--desde:{round(d.prima_antes * 100)};--hasta:{round(d.prima_despues * 100)}"></span>'
            f'<small> /mes</small></span>'
            f'<span class="ahorro">{_etiqueta_ahorro(d)}</span></div>{sube}</div>'
        )
    return f'<div class="grilla">{"".join(tarjetas)}</div>'


def rechazos(lista: list) -> str:
    filas = "".join(
        f'<div class="rechazo"><span class="x">{"✕" if d.estado == "Rechazado" else "↺"}</span>'
        f'<span class="id">{escape(d.id_chequeo)}<br>{escape(d.poliza)}</span><span>{escape(d.motivo)}</span></div>'
        for d in lista
    )
    return f'<div class="rechazos">{filas}</div>'


MEDALLA = {"Oro": "🥇", "Plata": "🥈", "Bronce": "🥉"}
ICONO_CHEQUEO = {"PROSTATA": "🧬", "MAMOGRAFIA": "🎗️", "PAPANICOLAOU": "🌸", "GLUCOSA": "🩸",
                 "PRESION": "🫀", "COLESTEROL": "🧪", "COLONOSCOPIA": "🔬"}


def ranking(asegurados: list[dict]) -> str:
    """Podio de los 3 con más puntos y tabla de posiciones con el avance al siguiente nivel."""
    from agente.gamificacion import siguiente_nivel

    orden = sorted(asegurados, key=lambda a: (-a["puntos"], a["prima_final"] - a["prima_base"], a["nombre"]))
    podio = ""
    if orden and orden[0]["puntos"] > 0:
        puestos = []
        tres = orden[:3] + [None] * (3 - len(orden[:3]))
        for clase, lugar, a in (("p2", "🥈", tres[1]), ("p1", "🏆", tres[0]), ("p3", "🥉", tres[2])):
            if a is None or a["puntos"] <= 0:
                puestos.append("<div></div>")
                continue
            ahorro = a["prima_base"] - a["prima_final"]
            puestos.append(
                f'<div class="puesto {clase}"><div class="lugar">{lugar}</div><div class="quien">{escape(a["nombre"])}</div>'
                f'<div class="puntaje">{a["puntos"]} pts</div><div class="dato">Nivel {a["nivel"]} · ahorra ${ahorro:.2f}/mes</div></div>'
            )
        podio = f'<div class="podio">{"".join(puestos)}</div>'

    filas = []
    for i, a in enumerate(orden, 1):
        sig = siguiente_nivel(a["puntos"])
        if sig:
            nivel, faltan, avance = sig
            meta = f"Le faltan {faltan} pts para {nivel}"
        else:
            avance, meta = 1.0, "Nivel máximo alcanzado"
        prima = (f'<s>${a["prima_base"]:.2f}</s>${a["prima_final"]:.2f}' if a["prima_final"] < a["prima_base"]
                 else f'${a["prima_final"]:.2f}')
        filas.append(
            f'<div class="fila-r"><div class="pos">{i}</div>'
            f'<div class="nom"><b>{MEDALLA.get(a["nivel"], "")} {escape(a["nombre"])}</b>'
            f'<span>{escape(a["poliza"])} · {a["puntos"]} pts · nivel {a["nivel"]}</span></div>'
            f'<div class="avance"><div class="barra"><i style="width:{max(avance, .02) * 100:.0f}%"></i></div>'
            f'<div class="meta">{meta}</div></div><div class="prima">{prima}</div></div>'
        )
    return f'{podio}<div class="ranking">{"".join(filas)}</div>'


def telefono(campanas: list[dict]) -> str:
    """Las campañas como notificaciones en la pantalla del celular del asegurado."""
    notifs = "".join(
        f'<div class="notif"><div class="app"><i></i>Mi Seguro de Salud<em>ahora</em></div>'
        f'<b>{ICONO_CHEQUEO.get(c["tipo_chequeo"], "💙")} {escape(c["nombre"])}</b><p>{escape(c["mensaje"])}</p></div>'
        for c in campanas[:4]
    )
    return (f'<div class="telefono"><div class="pantalla"><div class="hora">9:41</div>'
            f'<div class="fecha">Así lo recibe el asegurado</div>{notifs}</div></div>')


def linea_hospital(feed: list[dict], asegurados: list[dict], decisiones: list | None) -> str:
    """Los chequeos que reporta el hospital como una línea de tiempo, con su resultado si ya se procesaron."""
    por_poliza = {a["poliza"]: a for a in asegurados}
    resultado = {d.id_chequeo: d.estado for d in (decisiones or [])}
    clase = {"Premiado": "premiado", "Rechazado": "rechazado", "Ya premiado": "repetido"}
    eventos = []
    for i, ch in enumerate(reversed(feed)):
        a = por_poliza.get(ch["poliza"])
        quien = escape(a["nombre"]) if a else "Póliza no registrada"
        estado = resultado.get(ch["id_chequeo"], "Nuevo")
        eventos.append(
            f'<div class="evento" style="animation-delay:{min(i, 8) * .05:.2f}s">'
            f'<div class="ico">{ICONO_CHEQUEO.get(ch["tipo_chequeo"], "🩺")}</div>'
            f'<div><b>{quien}</b><span>{escape(CHEQUEOS.get(ch["tipo_chequeo"], ch["tipo_chequeo"]))} · '
            f'{escape(ch["poliza"])} · {escape(str(ch["fecha"]))}</span></div>'
            f'<span class="estado {clase.get(estado, "nuevo")}">{estado}</span></div>'
        )
    return f'<div class="linea">{"".join(eventos)}</div>'


def seccion(clase: str, icono: str, titulo: str, texto: str) -> str:
    return (f'<div class="seccion {clase}"><div class="icono">{icono}</div>'
            f"<div><h3>{titulo}</h3><p>{texto}</p></div></div>")


def privacidad(minimo: int) -> str:
    return (
        '<div class="privacidad">🔒 <b>Privacidad desde el diseño.</b> Los registros del hospital llegan sin nombre '
        "ni póliza. Al modelo de IA solo se le envían conteos agregados, y los grupos con menos de "
        f"{minimo} casos se ocultan para que nadie pueda ser identificado.</div>"
    )
