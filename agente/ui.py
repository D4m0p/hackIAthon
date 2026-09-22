"""Capa visual del panel: CSS e HTML. Sin lógica de negocio.

Identidad institucional de aseguradora de salud: serif cálida para los
títulos, sans humanista para el texto, azul petróleo de marca y verde para
todo lo que significa beneficio para el asegurado.

Todo texto que venga de fuera (nombres y mensajes que propone la IA, datos
del CRM) pasa por `escape` antes de entrar al HTML.
"""

import textwrap
from html import escape

from agente.catalogo import CHEQUEOS

# ── paleta ──────────────────────────────────────────────────────────────
# Los dos colores de serie de los gráficos (AZUL y CALIDO) están validados
# para daltonismo y contraste; no los cambie sin volver a comprobarlos.
AZUL = "#00719B"
CALIDO = "#BE6B26"
MARCA = "#12566A"
MARCA_HONDA = "#0C3F4E"
VERDE = "#35915F"
ROJO = "#8F2620"
AMBAR = "#A87515"
TINTA = "#16262C"

NIVEL_COLOR = {"Bronce": "#8E5321", "Plata": "#54707C", "Oro": "#8A6A12"}
NIVEL_FONDO = {"Bronce": "#F4E9DE", "Plata": "#E7EDEF", "Oro": "#F4EEDA"}


def _usd(v) -> str:
    return f"${float(v or 0):,.2f}"


def _pts(v) -> str:
    return f"{int(v or 0):,}".replace(",", " ")


def _cuenta(n: int) -> str:
    """Entero que cuenta desde cero al aparecer (contador CSS). El valor real queda en aria-label."""
    n = int(n or 0)
    return f'<var class="v-cnt" aria-hidden="true" style="--hasta:{n}"></var><span class="v-sr">{n}</span>'


def _cuenta_usd(hasta: float, desde: float | None = None) -> str:
    """Monto con centavos que se anima de `desde` a `hasta` (para montos menores a mil)."""
    h = round(float(hasta or 0) * 100)
    d = round(float(desde if desde is not None else 0) * 100)
    return (f'<var class="v-cnt-usd" aria-hidden="true" style="--desde:{d};--hasta:{h}"></var>'
            f'<span class="v-sr">{_usd(hasta)}</span>')


def _cuenta_grande(valor: float) -> str:
    """Monto grande en dólares enteros, con separador de miles, que sube hasta su valor."""
    v = round(abs(float(valor or 0)))
    signo = "−" if valor < 0 else ""
    if v >= 1_000_000:
        forma, piso = "g3", 1_000_000
    elif v >= 1_000:
        forma, piso = "g2", 1_000
    else:
        forma, piso = "g1", 0
    desde = max(piso, round(v * 0.55))
    return (f'{signo}<var class="v-cnt-g {forma}" aria-hidden="true" style="--desde:{desde};--hasta:{v}"></var>'
            f'<span class="v-sr">{signo}${v:,}</span>')


def _poblacion(c: dict) -> str:
    sexo = c.get("sexo", "Todos")
    quien = "Hombres y mujeres" if sexo == "Todos" else ("Mujeres" if sexo == "F" else "Hombres")
    return f"{quien} de {int(c['edad_min'])} a {int(c['edad_max'])} años"


def etiqueta(texto: str, ancho: int = 24) -> str:
    """Parte una etiqueta larga de un gráfico en varias líneas, para que quepa en pantallas angostas."""
    return textwrap.fill(str(texto), ancho)


def leyenda(items: list[tuple[str, str]]) -> str:
    """Leyenda de gráfico en HTML: (color, texto). Se acomoda sola en pantallas angostas."""
    return '<div class="v-leyenda">' + "".join(
        f'<span><i style="background:{escape(color)}"></i>{escape(texto)}</span>' for color, texto in items
    ) + '</div>'


CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&display=swap');

:root{
  --ground:#EFF4F5; --surface:#FFFFFF; --surface-2:#F5F9FA; --surface-3:#E4EDEF;
  --line:#DAE5E8; --line-2:#BECED3;
  --ink:#16262C; --ink-2:#47606A; --ink-3:#778F98;
  --marca:#12566A; --marca-honda:#0C3F4E; --marca-suave:#E3EEF1;
  --azul:#00719B; --calido:#BE6B26;
  --verde:#35915F; --verde-suave:#E5F1EA;
  --rojo:#8F2620; --rojo-suave:#F6E6E4;
  --ambar:#A87515; --ambar-suave:#F7EEDC;
  --bronce:#8E5321; --bronce-suave:#F4E9DE;
  --plata:#54707C;  --plata-suave:#E7EDEF;
  --oro:#8A6A12;    --oro-suave:#F4EEDA;
  --sombra:0 1px 2px rgba(18,42,52,.06), 0 12px 28px -20px rgba(18,42,52,.32);
  --serif:"Source Serif 4", Georgia, "Times New Roman", serif;
  --sans:"Source Sans 3", "Segoe UI", system-ui, sans-serif;
}

/* ── chrome de Streamlit ─────────────────────────────────────────────── */
.stApp{ background:var(--ground); }
/* Los íconos de Streamlit son una fuente de ligaduras: si se les cambia la
   familia tipográfica, el nombre del ícono (p. ej. "keyboard_arrow_right")
   se ve como texto encima de la etiqueta. Por eso quedan excluidos. */
html, body, [class*="st-"]:not([data-testid="stIconMaterial"]){ font-family:var(--sans); }
.block-container{ padding-top:2.1rem; padding-bottom:4rem; max-width:1180px; }
#MainMenu, footer{ visibility:hidden; }
[data-testid="stHeader"]{ background:transparent; }

h1,h2,h3,h4{ font-family:var(--serif) !important; letter-spacing:-.008em; color:var(--ink); }
.stApp p, .stApp li, .stApp label{ color:var(--ink-2); }
.stApp a{ color:var(--marca); }
/* Streamlit pinta TODO <p> con el color de texto general y eso pisa el claro
   que se hereda dentro de los bloques oscuros. Hay que devolvérselo. */
.stApp .v-piloto p, .stApp .v-carnet p, .stApp .v-memb p{ color:#EAF5F8; }
/* Lo mismo pasa con la etiqueta de los botones: el <p> de dentro tomaba el gris
   del texto general y en los botones turquesa no se leía. Hereda el color del botón. */
.stApp .stButton button p, .stApp .stFormSubmitButton button p, .stApp .stLinkButton a p{ color:inherit; }

[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--line); }
[data-testid="stSidebar"] h2{ font-size:1.15rem; }

/* pestañas: barra institucional, no pastillas de panel */
.stTabs [data-baseweb="tab-list"]{
  gap:2px; border-bottom:1px solid var(--line); background:transparent;
}
.stTabs [data-baseweb="tab"]{
  height:auto; padding:10px 16px; background:transparent; border-radius:0;
  font-family:var(--sans); font-size:.95rem; font-weight:500; color:var(--ink-3);
  border-bottom:2px solid transparent;
}
.stTabs [aria-selected="true"]{
  color:var(--ink) !important; font-weight:600; border-bottom-color:var(--marca) !important;
  background:transparent !important;
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ display:none; }

.stButton > button, .stFormSubmitButton > button, .stLinkButton > a{
  border-radius:9px; font-weight:600; font-family:var(--sans);
  border:1.5px solid var(--line-2); background:var(--surface); color:var(--marca);
  transition:border-color .15s, background .15s;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stLinkButton > a:hover{
  border-color:var(--marca); background:var(--marca-suave); color:var(--marca);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"]{
  background:var(--marca); border-color:var(--marca); color:#fff;
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover{
  background:var(--marca-honda); border-color:var(--marca-honda); color:#fff;
}

[data-testid="stMetric"]{
  background:var(--surface); border:1px solid var(--line); border-radius:12px;
  padding:16px 18px; box-shadow:var(--sombra);
}
[data-testid="stMetricLabel"] p{
  font-size:.78rem !important; text-transform:uppercase; letter-spacing:.1em;
  font-weight:600; color:var(--ink-3) !important;
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *{ white-space:normal !important; overflow-wrap:anywhere; }
[data-testid="stMetricLabel"]{ overflow:visible !important; text-overflow:clip !important; }
[data-testid="stMetricValue"]{
  font-family:var(--serif); font-weight:700; color:var(--marca); letter-spacing:-.02em;
}

[data-testid="stExpander"]{
  border:1px solid var(--line); border-radius:12px; background:var(--surface); overflow:hidden;
}
[data-testid="stExpander"] summary{ font-weight:600; color:var(--ink-2); }
[data-testid="stForm"]{
  border:1px solid var(--line); border-radius:14px; background:var(--surface);
  padding:22px; box-shadow:var(--sombra);
}
[data-testid="stDataFrame"], [data-testid="stJson"]{
  border:1px solid var(--line); border-radius:12px; overflow:hidden;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"]{ background:var(--marca); }
hr{ border-color:var(--line); }

/* ── portada ─────────────────────────────────────────────────────────── */
.v-kicker{
  text-transform:uppercase; letter-spacing:.13em; font-size:.74rem; font-weight:700;
  color:var(--marca); display:block; margin-bottom:12px;
}
.v-hero{
  background:radial-gradient(900px 340px at 88% -20%, var(--marca-suave), transparent 62%), var(--surface);
  border:1px solid var(--line); border-radius:18px; padding:42px 44px 36px;
  box-shadow:var(--sombra);
}
.v-hero h1{
  font-family:var(--serif); font-size:2.45rem; line-height:1.14; letter-spacing:-.022em;
  margin:0; font-weight:600; max-width:19ch; color:var(--ink);
}
.v-hero h1 em{ font-style:italic; color:var(--marca); }
.v-hero .sub{
  color:var(--ink-2); font-size:1.05rem; line-height:1.65; margin-top:16px; max-width:62ch;
}
.v-trust{
  display:flex; gap:42px; margin-top:30px; padding-top:22px;
  border-top:1px solid var(--line); flex-wrap:wrap;
}
.v-trust b{
  display:block; font-family:var(--serif); font-size:1.85rem; font-weight:700;
  letter-spacing:-.02em; color:var(--marca); font-variant-numeric:tabular-nums; line-height:1.15;
}
.v-trust span{ font-size:.86rem; color:var(--ink-3); display:block; margin-top:2px; }

/* ── encabezado de sección ───────────────────────────────────────────── */
.v-sec{ margin:6px 0 22px; padding-bottom:10px; border-bottom:1px solid var(--line-2); }
.v-sec h2{ font-family:var(--serif); font-size:1.5rem; margin:0; font-weight:600; }
.v-sec p{ color:var(--ink-2); font-size:.98rem; margin:7px 0 0; max-width:74ch; line-height:1.6; }

/* ── resultado del piloto ────────────────────────────────────────────── */
.v-piloto{
  background:linear-gradient(140deg,#17697C,#0C3B49); color:#EAF5F8;
  border-radius:16px; padding:26px 30px; box-shadow:var(--sombra);
}
.v-piloto h3{ font-family:var(--serif); color:#fff !important; margin:0 0 16px; font-size:1.3rem; }
.v-piloto .fila{ display:flex; gap:38px; flex-wrap:wrap; }
.v-piloto b{
  display:block; font-family:var(--serif); font-size:1.9rem; font-weight:700;
  font-variant-numeric:tabular-nums; line-height:1.15;
}
.v-piloto span{ font-size:.85rem; opacity:.82; display:block; margin-top:2px; }

/* ── tarjetas de campaña ─────────────────────────────────────────────── */
.v-camps{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,272px),1fr)); gap:16px; }
.v-camp{
  background:var(--surface); border:1px solid var(--line); border-radius:14px;
  overflow:hidden; display:flex; flex-direction:column; box-shadow:var(--sombra);
}
.v-camp .top{
  background:var(--marca-suave); padding:13px 18px; border-bottom:1px solid var(--line);
  font-size:.84rem; font-weight:600; color:var(--marca);
}
.v-camp .cuerpo{ padding:18px; display:flex; flex-direction:column; gap:12px; flex:1; }
.v-camp h4{ font-family:var(--serif); font-size:1.12rem; margin:0; line-height:1.3; font-weight:600; }
.v-camp .msg{
  color:var(--ink-2); font-size:.92rem; line-height:1.6; font-style:italic;
  border-left:3px solid var(--line-2); padding-left:13px;
}
.v-camp .datos{
  display:flex; justify-content:space-between; gap:4px 12px; flex-wrap:wrap; font-size:.88rem;
  border-top:1px solid var(--line); padding-top:11px; margin-top:auto;
}
.v-camp .datos span{ color:var(--ink-3); }
.v-camp .datos b{ color:var(--verde); font-variant-numeric:tabular-nums; }
.v-camp .porque{ font-size:.82rem; color:var(--ink-3); line-height:1.55; }

/* ── teléfono ────────────────────────────────────────────────────────── */
.v-fono{
  width:284px; max-width:100%; margin:0 auto; border-radius:34px; padding:16px 13px 22px;
  background:linear-gradient(160deg,#1C3038,#0E1D22); box-shadow:0 20px 46px -22px rgba(12,32,40,.75);
}
.v-fono .notch{ width:88px; height:5px; border-radius:3px; background:rgba(255,255,255,.22); margin:2px auto 14px; }
.v-fono .aviso{
  background:rgba(255,255,255,.96); border-radius:15px; padding:11px 13px; margin-bottom:9px;
}
.v-fono .de{
  font-size:.66rem; text-transform:uppercase; letter-spacing:.09em; color:var(--marca);
  font-weight:700; display:flex; justify-content:space-between;
}
.v-fono .de i{ font-style:normal; color:var(--ink-3); font-weight:500; letter-spacing:0; }
.v-fono h5{ font-family:var(--serif); font-size:.92rem; margin:5px 0 3px; color:var(--ink); font-weight:600; }
.v-fono p{ font-size:.79rem; color:var(--ink-2); margin:0; line-height:1.5; }

/* ── carnets de premiados ────────────────────────────────────────────── */
.v-carnets{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,286px),1fr)); gap:16px; }
.v-carnet{
  border-radius:16px; padding:20px 22px; color:#EAF5F8; position:relative; overflow:hidden;
  background:linear-gradient(142deg,#17697C,#0C3B49); box-shadow:var(--sombra);
}
.v-carnet::after{
  content:""; position:absolute; right:-52px; top:-52px; width:164px; height:164px;
  border-radius:50%; background:rgba(255,255,255,.07);
}
.v-carnet .cab{ display:flex; justify-content:space-between; align-items:center; position:relative; z-index:1; }
.v-carnet .marca{ font-size:.76rem; letter-spacing:.11em; text-transform:uppercase; opacity:.8; font-weight:700; }
.v-carnet .nivel{
  background:rgba(255,255,255,.18); border-radius:20px; padding:3px 11px;
  font-size:.72rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase;
}
.v-carnet h4{
  font-family:var(--serif); font-size:1.28rem; margin:18px 0 1px; color:#fff !important;
  position:relative; z-index:1; font-weight:600;
}
.v-carnet .pol{ font-size:.79rem; opacity:.7; letter-spacing:.12em; position:relative; z-index:1; }
.v-carnet .campana{
  font-size:.82rem; opacity:.85; margin-top:12px; position:relative; z-index:1; line-height:1.5;
}
.v-carnet .pie{
  display:flex; justify-content:space-between; align-items:flex-end; gap:14px;
  margin-top:16px; padding-top:13px; border-top:1px solid rgba(255,255,255,.2);
  position:relative; z-index:1;
}
.v-carnet .pie i{ font-style:normal; font-size:.7rem; opacity:.7; display:block; text-transform:uppercase; letter-spacing:.08em; }
.v-carnet .pie b{ font-family:var(--serif); font-size:1.24rem; font-variant-numeric:tabular-nums; }
.v-carnet .antes{ text-decoration:line-through; opacity:.55; font-size:.82rem; margin-right:7px; font-family:var(--sans); }
.v-carnet .ahora{ color:#9FE3BC; }
.v-carnet .subio{
  display:inline-block; margin-top:11px; background:rgba(159,227,188,.2); color:#B6ECCC;
  border-radius:20px; padding:3px 11px; font-size:.74rem; font-weight:700;
  position:relative; z-index:1;
}

/* ── rechazos ────────────────────────────────────────────────────────── */
.v-rech{ display:flex; flex-direction:column; gap:9px; }
.v-rech .item{
  display:flex; gap:14px; align-items:flex-start; background:var(--surface);
  border:1px solid var(--line); border-left:4px solid var(--rojo); border-radius:11px; padding:14px 16px;
}
.v-rech .item.dup{ border-left-color:var(--ambar); }
.v-rech .quien{ flex:0 1 210px; min-width:0; }
.v-rech .quien b{ display:block; color:var(--ink); font-size:.95rem; }
.v-rech .quien span{ font-size:.79rem; color:var(--ink-3); letter-spacing:.05em; }
.v-rech .motivo{ flex:1 1 0; min-width:0; font-size:.89rem; color:var(--ink-2); line-height:1.55; }
.v-rech .etiqueta{
  font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.06em;
  color:var(--rojo); background:var(--rojo-suave); border-radius:20px; padding:3px 11px;
  white-space:nowrap; margin-left:auto;
}
.v-rech .item.dup .etiqueta{ color:var(--ambar); background:var(--ambar-suave); }

/* ── línea del hospital ──────────────────────────────────────────────── */
.v-linea{ display:flex; flex-direction:column; }
.v-linea .ev{
  display:flex; gap:16px; align-items:flex-start; padding:13px 0;
  border-bottom:1px solid var(--line);
}
.v-linea .ev:last-child{ border-bottom:0; }
.v-linea .punto{
  width:11px; height:11px; border-radius:50%; margin-top:6px; flex:none;
  background:var(--line-2); box-shadow:0 0 0 3px var(--surface-3);
}
.v-linea .ev.ok .punto{ background:var(--verde); box-shadow:0 0 0 3px var(--verde-suave); }
.v-linea .ev.no .punto{ background:var(--rojo); box-shadow:0 0 0 3px var(--rojo-suave); }
.v-linea .ev.dup .punto{ background:var(--ambar); box-shadow:0 0 0 3px var(--ambar-suave); }
.v-linea .txt{ flex:1 1 0; min-width:0; }
.v-linea .txt b{ color:var(--ink); font-size:.95rem; }
.v-linea .txt span{ display:block; font-size:.85rem; color:var(--ink-3); margin-top:2px; }
.v-linea .fecha{ margin-left:auto; font-size:.8rem; color:var(--ink-3); white-space:nowrap; font-variant-numeric:tabular-nums; }

/* ── podio y tabla de posiciones ─────────────────────────────────────── */
.v-podio{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; align-items:end; margin-bottom:22px; }
.v-podio .p{
  background:var(--surface); border:1px solid var(--line); border-radius:14px;
  padding:18px 16px; text-align:center; box-shadow:var(--sombra);
}
.v-podio .p.uno{ border-color:var(--oro); box-shadow:0 0 0 3px var(--oro-suave), var(--sombra); }
.v-podio .medalla{
  width:34px; height:34px; border-radius:50%; margin:0 auto; display:flex; align-items:center;
  justify-content:center; font-family:var(--serif); font-weight:700; font-size:1rem; line-height:1;
  color:#fff; background:var(--plata);
}
.v-podio .p.uno .medalla{ background:var(--oro); }
.v-podio .p.tres .medalla{ background:var(--bronce); }
.v-podio h5{ font-family:var(--serif); font-size:1rem; margin:9px 0 2px; color:var(--ink); font-weight:600; }
.v-podio .pts{ font-family:var(--serif); font-size:1.5rem; font-weight:700; color:var(--marca); font-variant-numeric:tabular-nums; }
.v-podio .det{ font-size:.78rem; color:var(--ink-3); }

.v-tabla{ display:flex; flex-direction:column; gap:7px; }
.v-fila{
  display:grid; grid-template-columns:30px 1fr 128px 96px; gap:14px; align-items:center;
  background:var(--surface); border:1px solid var(--line); border-radius:11px; padding:11px 15px;
}
.v-fila .pos{ font-family:var(--serif); color:var(--ink-3); font-weight:700; font-variant-numeric:tabular-nums; }
.v-fila .nom b{ display:block; color:var(--ink); font-size:.95rem; }
.v-fila .nom span{ font-size:.78rem; color:var(--ink-3); letter-spacing:.05em; }
.v-fila .barra{ height:6px; background:var(--surface-3); border-radius:3px; overflow:hidden; }
.v-fila .barra i{ display:block; height:100%; background:var(--verde); border-radius:3px; }
.v-fila .barra + small{ font-size:.72rem; color:var(--ink-3); display:block; margin-top:4px; }
.v-fila .cifra{ text-align:right; }
.v-fila .cifra b{ font-family:var(--serif); font-size:1.05rem; font-variant-numeric:tabular-nums; color:var(--ink); }
.v-fila .cifra span{ display:block; font-size:.76rem; color:var(--verde); font-weight:600; }

.v-chip{
  display:inline-block; font-size:.72rem; font-weight:700; border-radius:20px;
  padding:2px 11px; letter-spacing:.04em;
}

/* ── membresía y anillo ──────────────────────────────────────────────── */
.v-memb{
  border-radius:18px; padding:26px 28px; color:#EAF5F8; position:relative; overflow:hidden;
  background:linear-gradient(142deg,#17697C,#0C3B49); box-shadow:var(--sombra);
}
.v-memb::after{
  content:""; position:absolute; right:-60px; top:-60px; width:196px; height:196px;
  border-radius:50%; background:rgba(255,255,255,.07);
}
.v-memb .cab{ display:flex; justify-content:space-between; align-items:center; position:relative; z-index:1; }
.v-memb .marca{ font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; opacity:.8; font-weight:700; }
.v-memb .nivel{
  background:rgba(255,255,255,.18); border-radius:20px; padding:4px 13px;
  font-size:.74rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
}
.v-memb h3{
  font-family:var(--serif); font-size:1.6rem; margin:24px 0 2px; color:#fff !important;
  position:relative; z-index:1; font-weight:600;
}
.v-memb .pol{ font-size:.85rem; opacity:.7; letter-spacing:.14em; position:relative; z-index:1; }
.v-memb .rejilla{
  display:grid; grid-template-columns:1fr 1fr; gap:3px 26px; margin-top:22px;
  padding-top:16px; border-top:1px solid rgba(255,255,255,.2); position:relative; z-index:1;
}
.v-memb .rejilla i{ font-style:normal; font-size:.71rem; opacity:.72; text-transform:uppercase; letter-spacing:.09em; font-weight:600; }
.v-memb .rejilla b{ font-family:var(--serif); font-size:1.35rem; font-variant-numeric:tabular-nums; }
.v-memb .rejilla b.baja{ color:#9FE3BC; }
.v-memb .rejilla b small{ font-size:.78rem; opacity:.6; font-family:var(--sans); text-decoration:line-through; margin-right:7px; }

.v-anillo{
  background:var(--surface); border:1px solid var(--line); border-radius:14px;
  padding:20px 22px; display:flex; align-items:center; gap:22px; flex-wrap:wrap; box-shadow:var(--sombra);
}
.v-anillo svg{ flex:none; }
.v-anillo .txt{ flex:1 1 200px; min-width:0; }
.v-anillo .txt b{ display:block; font-family:var(--serif); font-size:1.08rem; color:var(--ink); }
.v-anillo .txt span{ font-size:.88rem; color:var(--ink-2); line-height:1.55; display:block; margin-top:4px; }

/* ── recomendaciones e insignias ─────────────────────────────────────── */
.v-recos{ display:flex; flex-direction:column; gap:10px; }
.v-reco{
  background:var(--surface); border:1px solid var(--line); border-left:4px solid var(--verde);
  border-radius:11px; padding:14px 16px;
}
.v-reco b{ display:block; font-family:var(--serif); font-size:1.02rem; color:var(--ink); }
.v-reco .quien{ font-size:.82rem; color:var(--ink-3); margin-top:2px; }
.v-reco .gana{
  display:flex; gap:18px; margin-top:10px; padding-top:10px; border-top:1px dotted var(--line);
  font-size:.86rem; flex-wrap:wrap;
}
.v-reco .gana span{ color:var(--ink-3); }
.v-reco .gana b{ display:inline; font-family:var(--sans); color:var(--verde); font-weight:700; }
.v-vacio{
  background:var(--verde-suave); border-radius:11px; padding:15px 17px;
  font-size:.92rem; color:var(--ink-2); line-height:1.6;
}

.v-insig{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,140px),1fr)); gap:12px; }
.v-ins{
  background:var(--surface); border:1px solid var(--line); border-radius:12px;
  padding:15px 14px; text-align:center;
}
.v-ins.no{ opacity:.45; }
.v-ins .ic{ font-size:1.5rem; line-height:1; }
.v-ins b{ display:block; font-size:.88rem; color:var(--ink); margin-top:8px; font-weight:600; }
.v-ins span{ display:block; font-size:.75rem; color:var(--ink-3); margin-top:3px; line-height:1.45; }

/* ── impacto ─────────────────────────────────────────────────────────── */
.v-imp{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,168px),1fr)); gap:14px; }
.v-imp .t{
  background:var(--surface); border:1px solid var(--line); border-radius:13px;
  padding:17px 18px; box-shadow:var(--sombra);
}
.v-imp .t i{
  font-style:normal; font-size:.72rem; text-transform:uppercase; letter-spacing:.1em;
  color:var(--ink-3); font-weight:700; display:block; margin-bottom:6px;
}
.v-imp .t b{
  font-family:var(--serif); font-size:1.62rem; font-weight:700; color:var(--marca);
  letter-spacing:-.02em; font-variant-numeric:tabular-nums; display:block; line-height:1.15;
}
.v-imp .t.bueno b{ color:var(--verde); }
.v-imp .t span{ font-size:.78rem; color:var(--ink-3); display:block; margin-top:4px; line-height:1.45; }
.v-imp-pie{
  background:var(--marca-suave); border-radius:12px; padding:15px 18px; margin-top:14px;
  font-size:.92rem; color:var(--ink-2); line-height:1.6;
}

/* ── privacidad ──────────────────────────────────────────────────────── */
.v-priv{
  display:flex; gap:14px; background:var(--verde-suave); border-radius:13px;
  padding:17px 19px; margin-top:16px;
}
.v-priv .ic{ flex:none; width:22px; height:22px; margin-top:2px; color:var(--verde); }
.v-priv .ic svg{ display:block; width:100%; height:100%; }
.v-priv > div{ min-width:0; }

/* leyenda de los gráficos: en HTML para que se acomode sola en pantallas angostas */
.v-leyenda{ display:flex; flex-wrap:wrap; gap:6px 20px; margin:2px 0 6px; font-size:.86rem; color:var(--ink-2); }
.v-leyenda span{ display:inline-flex; align-items:center; gap:8px; }
.v-leyenda i{ width:12px; height:12px; border-radius:3px; flex:none; }
.v-priv b{ display:block; color:var(--ink); font-size:.98rem; margin-bottom:4px; font-weight:600; }
.v-priv p{ font-size:.9rem; color:var(--ink-2); margin:0; line-height:1.6; }

/* ── pantallas angostas ──────────────────────────────────────────────── */
.v-hero, .v-piloto, .v-carnet, .v-memb, .v-camp, .v-fila, .v-rech .item{ overflow-wrap:anywhere; }

@media (max-width: 820px){
  .v-hero{ padding:28px 22px; }
  .v-hero h1{ font-size:1.85rem; }
  .v-trust{ gap:22px 34px; }
  .v-podio{ gap:10px; }
  .v-podio .p{ padding:14px 8px; }
  .v-fila{ grid-template-columns:26px minmax(0,1fr) auto; gap:12px; }
  .v-fila .prog{ display:none; }
}

@media (max-width: 640px){
  .block-container{ padding-left:1rem; padding-right:1rem; padding-top:1.2rem; padding-bottom:3rem; }
  .stTabs [data-baseweb="tab"]{ padding:9px 12px; white-space:nowrap; }
  .v-hero{ padding:24px 18px 22px; border-radius:16px; }
  .v-hero h1{ font-size:1.6rem; max-width:none; }
  .v-hero .sub{ font-size:.98rem; margin-top:12px; }
  .v-trust{ margin-top:22px; padding-top:18px; gap:18px 20px; }
  .v-trust > div{ flex:1 1 40%; min-width:0; }
  .v-trust b{ font-size:1.55rem; }
  .v-sec h2{ font-size:1.3rem; }
  .v-piloto{ padding:22px 20px; }
  .v-piloto .fila{ display:grid; grid-template-columns:1fr 1fr; gap:18px 14px; }
  .v-piloto b{ font-size:1.6rem; }
  .v-carnet{ padding:18px 18px; }
  .v-memb{ padding:22px 20px; }
  .v-memb .rejilla{ gap:3px 14px; }
  .v-memb .rejilla b{ font-size:1.2rem; }
  .v-rech .item{ flex-direction:column; gap:8px; }
  .v-rech .quien{ flex:none; }
  .v-rech .etiqueta{ margin-left:0; order:-1; align-self:flex-start; }
  .v-linea .ev{ gap:12px; }
  .v-linea .fecha{ display:none; }
  .v-linea .txt span{ overflow-wrap:anywhere; }
  .v-podio .pts{ font-size:1.25rem; }
  .v-podio h5{ font-size:.9rem; }
  .v-anillo{ padding:18px; gap:16px; }
  .v-priv{ padding:15px 16px; }
  [data-testid="stForm"]{ padding:16px; }
}

@media (max-width: 460px){
  .v-imp{ grid-template-columns:1fr; }
  .v-podio{ grid-template-columns:1fr; }
  .v-podio .p{ display:flex; align-items:center; gap:14px; text-align:left; padding:12px 14px; }
  .v-podio .medalla{ margin:0; flex:none; }
  .v-podio .p .txt{ min-width:0; }
}
/* ══ movimiento con propósito ══════════════════════════════════════════
   Todo se apaga con prefers-reduced-motion (regla al final del bloque). */

/* pestañas: Streamlit 1.64 ya no usa data-baseweb="tab"; mismo estilo institucional */
.stTabs [role="tablist"]{ gap:2px; border-bottom:1px solid var(--line); background:transparent; }
.stTabs [data-testid="stTab"]{
  height:auto; padding:10px 16px; background:transparent; border-radius:0; position:relative;
  font-family:var(--sans); font-size:.95rem; font-weight:500; color:var(--ink-3); transition:color .25s;
}
.stTabs [data-testid="stTab"] p{ color:inherit; }
.stTabs [data-testid="stTab"]::after{
  content:""; position:absolute; left:12px; right:12px; bottom:-1px; height:2px; background:var(--marca);
  transform:scaleX(0); transition:transform .35s cubic-bezier(.22,1,.36,1);
}
.stTabs [data-testid="stTab"]:hover{ color:var(--ink); }
.stTabs [data-testid="stTab"][aria-selected="true"]{ color:var(--ink); font-weight:600; }
.stTabs [data-testid="stTab"][aria-selected="true"]::after{ transform:scaleX(1); }
.stTabs .react-aria-SelectionIndicator{ display:none; }

/* cambio de sección: el contenido entra con un desvanecido corto */
@keyframes v-entrar{ from{ opacity:0; transform:translateY(14px); } to{ opacity:1; transform:none; } }
.stTabs [role="tabpanel"]{ animation:v-entrar .55s cubic-bezier(.22,1,.36,1) both; }
.v-hero, .v-piloto{ animation:v-entrar .7s cubic-bezier(.22,1,.36,1) both; }

/* tarjetas en cascada */
.v-camps > *, .v-carnets > *, .v-recos > *, .v-insig > *, .v-imp > *, .v-tabla > *, .v-rech > *{
  animation:v-entrar .6s cubic-bezier(.22,1,.36,1) both;
}
.v-camps > :nth-child(2), .v-carnets > :nth-child(2), .v-recos > :nth-child(2), .v-insig > :nth-child(2), .v-imp > :nth-child(2), .v-tabla > :nth-child(2), .v-rech > :nth-child(2){ animation-delay:.06s; }
.v-camps > :nth-child(3), .v-carnets > :nth-child(3), .v-recos > :nth-child(3), .v-insig > :nth-child(3), .v-imp > :nth-child(3), .v-tabla > :nth-child(3), .v-rech > :nth-child(3){ animation-delay:.12s; }
.v-camps > :nth-child(4), .v-carnets > :nth-child(4), .v-recos > :nth-child(4), .v-insig > :nth-child(4), .v-imp > :nth-child(4), .v-tabla > :nth-child(4), .v-rech > :nth-child(4){ animation-delay:.18s; }
.v-camps > :nth-child(5), .v-carnets > :nth-child(5), .v-recos > :nth-child(5), .v-insig > :nth-child(5), .v-imp > :nth-child(5), .v-tabla > :nth-child(5), .v-rech > :nth-child(5){ animation-delay:.24s; }
.v-camps > :nth-child(n+6), .v-carnets > :nth-child(n+6), .v-recos > :nth-child(n+6), .v-insig > :nth-child(n+6), .v-imp > :nth-child(n+6), .v-tabla > :nth-child(n+6), .v-rech > :nth-child(n+6){ animation-delay:.3s; }

/* tarjetas que responden al puntero */
.v-camp, .v-carnet, .v-reco, .v-ins, .v-imp .t, .v-podio .p, [data-testid="stMetric"]{
  transition:transform .3s cubic-bezier(.22,1,.36,1), box-shadow .3s;
}
.v-camp:hover, .v-carnet:hover, .v-reco:hover, .v-ins:hover, .v-imp .t:hover, .v-podio .p:hover, [data-testid="stMetric"]:hover{
  transform:translateY(-3px);
  box-shadow:0 2px 4px rgba(18,42,52,.06), 0 22px 40px -22px rgba(18,42,52,.45);
}

/* encabezado: trazo de electrocardiograma */
.v-hero{ position:relative; overflow:hidden; }
.v-ecg{ position:absolute; right:36px; top:46px; width:min(44%,500px); height:auto; pointer-events:none; overflow:visible; }
.v-ecg path{ fill:none; stroke-linecap:round; stroke-linejoin:round; }
.v-ecg .base{ stroke:var(--line); stroke-width:2; }
.v-ecg .traza{
  stroke:var(--marca); stroke-width:3; stroke-dasharray:1; stroke-dashoffset:1;
  animation:v-trazar 2.2s .35s cubic-bezier(.65,0,.35,1) forwards;
}
@keyframes v-trazar{ to{ stroke-dashoffset:0; } }
.v-ecg .pulso{
  fill:var(--verde); filter:drop-shadow(0 0 6px rgba(53,145,95,.8));
  offset-rotate:0deg; offset-distance:0%; opacity:0;
  animation:v-recorrer 3.6s 2.6s linear infinite;
}
@keyframes v-recorrer{ 0%{ offset-distance:0%; opacity:0; } 6%{ opacity:1; } 90%{ opacity:1; } 100%{ offset-distance:100%; opacity:0; } }
@media (max-width: 900px){
  .v-ecg{ position:relative; right:auto; top:auto; width:100%; max-width:460px; display:block; margin:18px 0 -6px; }
}

/* contadores: se anima un entero registrado y se muestra con contadores CSS */
@property --v-n{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-c{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-d{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-g{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-k{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-u{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-m{ syntax:'<integer>'; inherits:false; initial-value:0; }
@property --v-kk{ syntax:'<integer>'; inherits:false; initial-value:0; }
@counter-style v-tres{ system:extends decimal; pad:3 "0"; }
/* texto solo para lectores de pantalla: el número real detrás de cada contador */
.v-sr{ position:absolute !important; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
.v-cnt, .v-cnt-usd, .v-cnt-g{ font:inherit; color:inherit; font-style:normal; }

.v-cnt{ --v-n:var(--hasta); counter-reset:vn var(--v-n); animation:v-contar-n 1.3s .25s cubic-bezier(.16,1,.3,1) both; }
.v-cnt::before{ content:counter(vn); }
@keyframes v-contar-n{ from{ --v-n:0; } }

.v-cnt-usd{
  --v-c:var(--hasta); --v-d:calc((var(--v-c) - 50) / 100);
  counter-reset:vd var(--v-d) vc calc(var(--v-c) - var(--v-d) * 100);
  animation:v-contar-usd 1.8s .45s cubic-bezier(.16,1,.3,1) both;
}
.v-cnt-usd::before{ content:"$" counter(vd) "." counter(vc, decimal-leading-zero); }
@keyframes v-contar-usd{ from{ --v-c:var(--desde); } }

.v-cnt-g{
  --v-g:var(--hasta);
  --v-k:calc((var(--v-g) - 500) / 1000); --v-u:calc(var(--v-g) - var(--v-k) * 1000);
  --v-m:calc((var(--v-k) - 500) / 1000); --v-kk:calc(var(--v-k) - var(--v-m) * 1000);
  counter-reset:vg var(--v-g) vk var(--v-k) vu var(--v-u) vm var(--v-m) vkk var(--v-kk);
  animation:v-contar-g 1.9s .3s cubic-bezier(.16,1,.3,1) both;
}
.v-cnt-g.g1::before{ content:"$" counter(vg); }
.v-cnt-g.g2::before{ content:"$" counter(vk) "," counter(vu, v-tres); }
.v-cnt-g.g3::before{ content:"$" counter(vm) "," counter(vkk, v-tres) "," counter(vu, v-tres); }
@keyframes v-contar-g{ from{ --v-g:var(--desde); } }

/* carnet: la prima vieja se tacha y la nueva baja; un reflejo cruza la tarjeta una vez */
.v-carnet .antes{ animation:v-tachar .5s .3s ease-out both; }
@keyframes v-tachar{ from{ text-decoration-color:transparent; opacity:1; } }
.v-carnet .ahora{ display:inline-block; }
.v-carnet::before, .v-memb::before{
  content:""; position:absolute; inset:0; pointer-events:none; z-index:2;
  background:linear-gradient(110deg, transparent 38%, rgba(255,255,255,.16) 50%, transparent 62%);
  background-size:260% 100%; background-position:130% 0;
}
.v-carnet::before{ animation:v-reflejo 1.6s .5s ease-out both; }
.v-memb::before{ animation:v-reflejo 2.4s .6s ease-in-out infinite; animation-delay:.6s; }
@keyframes v-reflejo{ to{ background-position:-40% 0; } }
.v-carnet .subio{ animation:v-entrar .5s 1.9s cubic-bezier(.22,1,.36,1) both; }

/* membresía: entra con un leve giro */
.v-memb{ animation:v-girar .9s cubic-bezier(.22,1,.36,1) both; transform-origin:left center; }
@keyframes v-girar{ from{ opacity:0; transform:perspective(900px) rotateY(-24deg) translateX(-12px); } }

/* gamificación: podio que sube, barras y anillo que se llenan */
.v-podio .p{ animation:v-subir .8s cubic-bezier(.34,1.35,.64,1) both; }
.v-podio .p:nth-child(1){ animation-delay:.1s; }
.v-podio .p:nth-child(2){ animation-delay:.25s; }
.v-podio .p:nth-child(3){ animation-delay:.4s; }
@keyframes v-subir{ from{ opacity:0; transform:translateY(34px); } }
.v-podio .p.uno .medalla{ animation:v-latido 2.4s 1.2s ease-in-out infinite; }
@keyframes v-latido{ 0%,100%{ box-shadow:0 0 0 0 rgba(138,106,18,.45); } 50%{ box-shadow:0 0 0 9px rgba(138,106,18,0); } }
.v-fila .barra i{ transform-origin:left; animation:v-llenar 1.1s .35s cubic-bezier(.22,1,.36,1) both; }
@keyframes v-llenar{ from{ transform:scaleX(0); } }
.v-anillo .arco{ animation:v-arco 1.4s .3s cubic-bezier(.22,1,.36,1) both; }
@keyframes v-arco{ from{ stroke-dashoffset:213.6; } }

/* impacto: la cifra neta respira una vez al llegar */
.v-imp .t.bueno b{ animation:v-resaltar 1s 2.1s ease-out both; }
@keyframes v-resaltar{ 0%{ text-shadow:0 0 0 rgba(53,145,95,0); } 40%{ text-shadow:0 0 18px rgba(53,145,95,.45); } 100%{ text-shadow:0 0 0 rgba(53,145,95,0); } }

@media (prefers-reduced-motion: reduce){ *{ transition:none !important; animation:none !important; } }
</style>"""


# ── portada ─────────────────────────────────────────────────────────────

def hero(n_campanas: int, n_con_descuento: int, ahorro: float) -> str:
    return (
        '<div class="v-hero">'
        '<span class="v-kicker">Programa Bienestar Preventivo</span>'
        '<h1>Hágase el chequeo a tiempo y <em>su prima baja</em>.</h1>'
        '<p class="sub">Revisamos cada mes qué está enfermando a nuestros asegurados, abrimos '
        'campañas de prevención para los casos más frecuentes y le devolvemos el gesto: cada '
        'chequeo que usted cumple suma puntos, sube de nivel y descuenta su cuota mensual.</p>'
        '<div class="v-trust">'
        f'<div><b>{_cuenta(n_campanas)}</b><span>campañas abiertas</span></div>'
        f'<div><b>{_cuenta(n_con_descuento)}</b><span>asegurados con descuento</span></div>'
        f'<div><b>{_cuenta_usd(ahorro)}</b><span>menos de prima al mes</span></div>'
        f'</div>{_ECG}</div>'
    )


# Trazo de electrocardiograma del encabezado: se dibuja una vez y un punto de luz lo recorre.
_TRAZO = "M0 96 H150 L166 96 L178 78 L190 96 H214 L226 110 L244 18 L264 150 L282 96 H330 L346 84 L362 96 H560"
_ECG = (
    '<svg class="v-ecg" viewBox="0 0 560 170" aria-hidden="true" preserveAspectRatio="xMidYMid meet">'
    f'<path class="base" d="{_TRAZO}"/><path class="traza" d="{_TRAZO}" pathLength="1"/>'
    f'<circle class="pulso" r="5" style="offset-path:path(\'{_TRAZO}\')"/></svg>'
)


def seccion(clave: str, titulo: str, subtitulo: str) -> str:
    """Encabezado de sección. Sin emojis: la identidad institucional no los usa como marcadores."""
    return (
        f'<div class="v-sec" id="{escape(str(clave))}">'
        f'<h2>{escape(titulo)}</h2>'
        f'<p>{escape(subtitulo)}</p>'
        '</div>'
    )


def resumen_piloto(r: dict) -> str:
    suben = int(r.get("suben", 0))
    frase = "Nadie cambió de nivel en esta tanda." if not suben else (
        "1 asegurado subió de nivel." if suben == 1 else f"{suben} asegurados subieron de nivel.")
    return (
        '<div class="v-piloto">'
        '<h3>El agente cerró su ciclo completo</h3>'
        '<div class="fila">'
        f'<div><b>{_cuenta(r.get("campanas", 0))}</b><span>campañas publicadas</span></div>'
        f'<div><b>{_cuenta(r.get("premiados", 0))}</b><span>chequeos premiados</span></div>'
        f'<div><b>{_cuenta(suben)}</b><span>subieron de nivel</span></div>'
        f'<div><b>{_cuenta_usd(r.get("ahorro", 0))}</b><span>menos de prima al mes</span></div>'
        '</div>'
        f'<p style="margin:16px 0 0;opacity:.82;font-size:.9rem">{frase} '
        'Todo quedó escrito en el CRM.</p>'
        '</div>'
    )


def privacidad(minimo: int) -> str:
    return (
        '<div class="v-priv">'
        '<span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="4.5" y="10.5" width="15" height="10" rx="2.2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>'
        '</svg></span><div>'
        '<b>Por qué esto no identifica a nadie</b>'
        '<p>Los diagnósticos llegan sin nombre y sin número de póliza. Los grupos de sexo y edad '
        f'con menos de {int(minimo)} casos se ocultan, porque en un grupo tan pequeño decir el '
        'diagnóstico sería casi decir el nombre. Al modelo de IA solo le llegan conteos agregados: '
        'nunca una fila de una persona.</p>'
        '</div></div>'
    )


# ── campañas ────────────────────────────────────────────────────────────

def campanas(lista: list[dict], chequeos: dict | None = None) -> str:
    nombres = chequeos or CHEQUEOS
    tarjetas = []
    for c in lista:
        tipo = c.get("tipo_chequeo", "")
        justif = c.get("justificacion") or c.get("diagnostico") or ""
        tarjetas.append(
            '<article class="v-camp">'
            f'<div class="top">{escape(_poblacion(c))}</div>'
            '<div class="cuerpo">'
            f'<h4>{escape(str(c.get("nombre", "")))}</h4>'
            f'<p class="msg">«{escape(str(c.get("mensaje", "")))}»</p>'
            f'<p class="porque">{escape(str(justif))}</p>'
            '<div class="datos">'
            f'<span>{escape(nombres.get(tipo, tipo))}</span>'
            f'<b>{int(c.get("puntos", 0))} puntos</b>'
            '</div></div></article>'
        )
    return f'<div class="v-camps">{"".join(tarjetas)}</div>'


def telefono(propuestas: list[dict]) -> str:
    avisos = []
    for i, c in enumerate(propuestas[:4]):
        cuando = "ahora" if i == 0 else f"hace {i * 3} min"
        avisos.append(
            '<div class="aviso">'
            f'<div class="de">Bienestar Preventivo <i>{cuando}</i></div>'
            f'<h5>{escape(str(c.get("nombre", "")))}</h5>'
            f'<p>{escape(str(c.get("mensaje", ""))[:120])}…</p>'
            '</div>'
        )
    return f'<div class="v-fono"><div class="notch"></div>{"".join(avisos)}</div>'


# ── premios ─────────────────────────────────────────────────────────────

def carnets(premiados: list) -> str:
    tarjetas = []
    for d in premiados:
        a = d.asegurado or {}
        nivel = d.nivel_nuevo or a.get("nivel", "Bronce")
        campana = (d.campana or {}).get("nombre", "")
        if d.prima_antes is not None and d.prima_despues is not None and d.prima_despues < d.prima_antes:
            prima = (f'<span class="antes">{_usd(d.prima_antes)}</span>'
                     f'<span class="ahora">{_cuenta_usd(d.prima_despues, d.prima_antes)}</span>')
        else:
            prima = _usd(d.prima_despues if d.prima_despues is not None else a.get("prima_final", 0))
        subio = '<span class="subio">Subió a nivel ' + escape(nivel) + '</span>' if d.subio_de_nivel else ''
        tarjetas.append(
            '<article class="v-carnet">'
            '<div class="cab">'
            '<span class="marca">Bienestar Preventivo</span>'
            f'<span class="nivel">{escape(nivel)}</span>'
            '</div>'
            f'<h4>{escape(str(a.get("nombre", d.poliza)))}</h4>'
            f'<div class="pol">{escape(str(d.poliza))}</div>'
            f'<p class="campana">{escape(CHEQUEOS.get(d.tipo, d.tipo))} · {escape(str(campana))}</p>'
            '<div class="pie">'
            f'<div><i>Puntos ganados</i><b>+{int(d.puntos)}</b></div>'
            f'<div style="text-align:right"><i>Cuota mensual</i><b>{prima}</b></div>'
            '</div>'
            f'{subio}'
            '</article>'
        )
    return f'<div class="v-carnets">{"".join(tarjetas)}</div>'


def rechazos(otros: list) -> str:
    filas = []
    for d in otros:
        dup = d.estado == "Ya premiado"
        a = d.asegurado or {}
        nombre = a.get("nombre") or "Póliza no encontrada"
        filas.append(
            f'<div class="item{" dup" if dup else ""}">'
            '<div class="quien">'
            f'<b>{escape(str(nombre))}</b>'
            f'<span>{escape(str(d.poliza))} · {escape(CHEQUEOS.get(d.tipo, d.tipo))}</span>'
            '</div>'
            f'<div class="motivo">{escape(str(d.motivo))}</div>'
            f'<span class="etiqueta">{escape(d.estado)}</span>'
            '</div>'
        )
    return f'<div class="v-rech">{"".join(filas)}</div>'


def linea_hospital(feed: list[dict], asegurados: list[dict], decisiones=None) -> str:
    por_poliza = {a["poliza"]: a for a in asegurados}
    estado_por_id = {}
    if decisiones:
        for d in decisiones:
            estado_por_id[d.id_chequeo] = d.estado

    eventos = []
    for ch in sorted(feed, key=lambda c: str(c.get("fecha", "")), reverse=True):
        estado = estado_por_id.get(ch["id_chequeo"])
        clase = {"Premiado": "ok", "Rechazado": "no", "Ya premiado": "dup"}.get(estado, "")
        a = por_poliza.get(ch["poliza"])
        quien = a["nombre"] if a else "Póliza no registrada"
        detalle = CHEQUEOS.get(ch["tipo_chequeo"], ch["tipo_chequeo"])
        if estado:
            detalle += f" · {estado.lower()}"
        eventos.append(
            f'<div class="ev {clase}">'
            '<span class="punto"></span>'
            '<div class="txt">'
            f'<b>{escape(str(quien))}</b>'
            f'<span>{escape(detalle)}</span>'
            '</div>'
            f'<span class="fecha">{escape(str(ch.get("fecha", "")))}</span>'
            '</div>'
        )
    if not eventos:
        return '<div class="v-vacio">El hospital todavía no ha reportado chequeos este mes.</div>'
    return f'<div class="v-linea">{"".join(eventos)}</div>'


# ── CRM ─────────────────────────────────────────────────────────────────

def _chip_nivel(nivel: str) -> str:
    color = NIVEL_COLOR.get(nivel, "#54707C")
    fondo = NIVEL_FONDO.get(nivel, "#E7EDEF")
    return f'<span class="v-chip" style="color:{color};background:{fondo}">{escape(nivel)}</span>'


def ranking(asegurados: list[dict]) -> str:
    orden = sorted(asegurados, key=lambda a: (-a.get("puntos", 0), a.get("nombre", "")))
    lugar = ["uno", "dos", "tres"]
    podio = []
    for i, a in enumerate(orden[:3]):
        podio.append(
            f'<div class="p {lugar[i]}">'
            f'<div class="medalla">{i + 1}</div>'
            '<div class="txt">'
            f'<h5>{escape(str(a.get("nombre", "")))}</h5>'
            f'<div class="pts">{_pts(a.get("puntos"))}</div>'
            f'<div class="det">puntos · {escape(str(a.get("nivel", "Bronce")))}</div>'
            '</div></div>'
        )

    filas = []
    for i, a in enumerate(orden, start=1):
        puntos = int(a.get("puntos", 0))
        meta = 200 if puntos < 200 else max(puntos, 200)
        avance = min(100, round(puntos / meta * 100)) if meta else 0
        falta = ("nivel máximo alcanzado" if puntos >= 200
                 else f"faltan {100 - puntos} para Plata" if puntos < 100
                 else f"faltan {200 - puntos} para Oro")
        ahorro = float(a.get("prima_base", 0)) - float(a.get("prima_final", 0))
        linea_ahorro = f'<span>−{_usd(ahorro)} al mes</span>' if ahorro > 0 else ''
        filas.append(
            '<div class="v-fila">'
            f'<div class="pos">{i}</div>'
            '<div class="nom">'
            f'<b>{escape(str(a.get("nombre", "")))} {_chip_nivel(str(a.get("nivel", "Bronce")))}</b>'
            f'<span>{escape(str(a.get("poliza", "")))}</span>'
            '</div>'
            f'<div class="prog"><div class="barra"><i style="width:{avance}%"></i></div><small>{escape(falta)}</small></div>'
            f'<div class="cifra"><b>{_pts(puntos)}</b>{linea_ahorro}</div>'
            '</div>'
        )
    return f'<div class="v-podio">{"".join(podio)}</div><div class="v-tabla">{"".join(filas)}</div>'


# ── perfil ──────────────────────────────────────────────────────────────

def membresia(a: dict) -> str:
    base = float(a.get("prima_base", 0))
    final = float(a.get("prima_final", base))
    if final < base:
        prima = f'<b class="baja"><small>{_usd(base)}</small>{_usd(final)}</b>'
    else:
        prima = f'<b>{_usd(final)}</b>'
    return (
        '<div class="v-memb">'
        '<div class="cab">'
        '<span class="marca">Programa Bienestar Preventivo</span>'
        f'<span class="nivel">{escape(str(a.get("nivel", "Bronce")))}</span>'
        '</div>'
        f'<h3>{escape(str(a.get("nombre", "")))}</h3>'
        f'<div class="pol">{escape(str(a.get("poliza", "")))}</div>'
        '<div class="rejilla">'
        '<i>Puntos acumulados</i><i>Cuota mensual</i>'
        f'<b>{_pts(a.get("puntos"))}</b>{prima}'
        '</div></div>'
    )


def anillo(a: dict) -> str:
    puntos = int(a.get("puntos", 0))
    if puntos >= 200:
        meta, falta, titulo = 200, 0, "Nivel Oro alcanzado"
        texto = "Ya tiene el 10 % de descuento, el máximo del programa. Sus puntos siguen sumando."
    elif puntos >= 100:
        meta, falta, titulo = 200, 200 - puntos, "Camino al nivel Oro"
        texto = f"Le faltan {falta} puntos para llegar a Oro y pasar del 5 % al 10 % de descuento."
    else:
        meta, falta, titulo = 100, 100 - puntos, "Camino al nivel Plata"
        texto = f"Le faltan {falta} puntos para llegar a Plata y empezar a pagar 5 % menos."

    avance = min(1.0, puntos / meta) if meta else 0.0
    radio, circ = 34, 2 * 3.14159 * 34
    ofs = circ * (1 - avance)
    anillo_svg = (
        '<svg width="86" height="86" viewBox="0 0 86 86" aria-hidden="true">'
        f'<circle cx="43" cy="43" r="{radio}" fill="none" stroke="#E4EDEF" stroke-width="9"/>'
        f'<circle cx="43" cy="43" r="{radio}" fill="none" stroke="{VERDE}" stroke-width="9"'
        f' class="arco" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{ofs:.1f}"'
        ' transform="rotate(-90 43 43)"/>'
        f'<text x="43" y="49" text-anchor="middle" font-size="19" font-weight="700"'
        f' font-family="Source Serif 4, Georgia, serif" fill="{TINTA}">{round(avance * 100)}%</text>'
        '</svg>'
    )
    return (
        f'<div class="v-anillo">{anillo_svg}'
        f'<div class="txt"><b>{escape(titulo)}</b><span>{escape(texto)}</span></div></div>'
    )


def recomendaciones(lista: list[dict]) -> str:
    if not lista:
        return ('<div class="v-vacio">Por ahora no hay ninguna campaña abierta que le corresponda, '
                'o ya cumplió todas las que aplican a su edad. Le avisaremos cuando se abra una nueva.</div>')
    bloques = []
    for r in lista:
        c = r["campana"]
        extra = (f'<span>Su cuota bajaría <b>{_usd(r["ahorro_extra"])}</b> al mes</span>'
                 if r.get("ahorro_extra", 0) > 0 else
                 '<span>Acerca su próximo nivel de descuento</span>')
        sube = f'<span>Pasaría a nivel <b>{escape(str(r["nivel_nuevo"]))}</b></span>' if r.get("sube") else ''
        bloques.append(
            '<div class="v-reco">'
            f'<b>{escape(str(c.get("nombre", "")))}</b>'
            f'<div class="quien">{escape(CHEQUEOS.get(c.get("tipo_chequeo", ""), ""))} · {escape(_poblacion(c))}</div>'
            '<div class="gana">'
            f'<span>Le sumaría <b>{int(r.get("puntos", 0))} puntos</b></span>'
            f'{extra}{sube}'
            '</div></div>'
        )
    return f'<div class="v-recos">{"".join(bloques)}</div>'


def insignias(lista: list[dict]) -> str:
    tarjetas = []
    for i in lista:
        ganada = bool(i.get("ganada"))
        tarjetas.append(
            f'<div class="v-ins{"" if ganada else " no"}">'
            f'<div class="ic">{escape(str(i.get("icono", "")))}</div>'
            f'<b>{escape(str(i.get("nombre", "")))}</b>'
            f'<span>{escape(str(i.get("como", "")))}</span>'
            '</div>'
        )
    return f'<div class="v-insig">{"".join(tarjetas)}</div>'


# ── impacto económico ───────────────────────────────────────────────────

def impacto(res: dict, n_asegurados: int, participacion: float) -> str:
    roi = float(res.get("roi", 0))
    neto = float(res.get("neto", 0))
    tiles = [
        ("Ahorro en tratamientos", _cuenta_grande(res.get("ahorro", 0)),
         "por casos detectados a tiempo", True),
        ("Costo de los chequeos", _usd(res.get("chequeos", 0)),
         "lo que paga la aseguradora por tamizar", False),
        ("Descuentos otorgados", _usd(res.get("descuentos", 0)),
         "menor prima para quien se cuida", False),
        ("Resultado neto al año", _cuenta_grande(neto),
         "ahorro menos costos del programa", neto >= 0),
        ("Retorno por dólar", f"{roi:,.2f}×",
         "se recupera por cada dólar invertido", roi >= 1),
        ("Casos detectados a tiempo", f"{float(res.get('casos', 0)):,.0f}",
         "antes de que se vuelvan caros", True),
    ]
    bloques = "".join(
        f'<div class="t{" bueno" if bueno else ""}"><i>{escape(t)}</i><b>{v if "v-cnt" in v else escape(v)}</b>'
        f'<span>{escape(s)}</span></div>'
        for t, v, s, bueno in tiles
    )
    cuantos = f"{int(n_asegurados):,}".replace(",", " ")
    veredicto = (
        f'Con {cuantos} asegurados y una participación del {participacion * 100:.0f} %, '
        f'el programa {"se paga solo y deja" if neto >= 0 else "todavía no se paga: le falta"} '
        f'{_usd(abs(neto))} al año. La prevención se cobra sola cuando evita un tratamiento tardío.'
    )
    return f'<div class="v-imp">{bloques}</div><div class="v-imp-pie">{escape(veredicto)}</div>'
