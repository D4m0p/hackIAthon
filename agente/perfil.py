"""Perfil del asegurado: insignias ganadas y recomendaciones personales del agente."""

from agente.gamificacion import aplica_a, premiar, prima_final

INSIGNIAS = [  # (clave, ícono, nombre, cómo se gana)
    ("primer", "🌱", "Primer paso", "Completar el primer chequeo preventivo"),
    ("corazon", "🫀", "Guardián del corazón", "Chequeo de presión o de colesterol"),
    ("azucar", "🩸", "Azúcar bajo control", "Chequeo de glucosa"),
    ("temprana", "🎗️", "Detección temprana", "Chequeo de próstata, mama, cuello uterino o colon"),
    ("constancia", "🔥", "Constancia", "Dos o más chequeos cumplidos"),
    ("plata", "🥈", "Nivel Plata", "Llegar a 100 puntos"),
    ("oro", "🥇", "Nivel Oro", "Llegar a 200 puntos"),
]

_TEMPRANA = {"PROSTATA", "MAMOGRAFIA", "PAPANICOLAOU", "COLONOSCOPIA"}


def insignias(asegurado: dict, tipos_cumplidos: list[str]) -> list[dict]:
    """Todas las insignias, marcando cuáles ganó este asegurado."""
    t = set(tipos_cumplidos)
    ganadas = {
        "primer": len(tipos_cumplidos) >= 1,
        "corazon": bool(t & {"PRESION", "COLESTEROL"}),
        "azucar": "GLUCOSA" in t,
        "temprana": bool(t & _TEMPRANA),
        "constancia": len(tipos_cumplidos) >= 2,
        "plata": asegurado["puntos"] >= 100,
        "oro": asegurado["puntos"] >= 200,
    }
    return [{"clave": k, "icono": i, "nombre": n, "como": c, "ganada": ganadas[k]} for k, i, n, c in INSIGNIAS]


def recomendaciones(asegurado: dict, campanas_activas: list[dict], tipos_cumplidos: list[str]) -> list[dict]:
    """Campañas activas para las que califica y que aún no cumplió, con lo que ganaría al hacerlas."""
    salida = []
    for c in campanas_activas:
        if c["tipo_chequeo"] in tipos_cumplidos or not aplica_a(c, asegurado["sexo"], asegurado["edad"]):
            continue
        r = premiar(asegurado["puntos"], asegurado["prima_base"], c["puntos"])
        salida.append({
            "campana": c, "puntos": c["puntos"], "nivel_nuevo": r.nivel, "sube": r.subio_de_nivel,
            "ahorro_extra": round(asegurado["prima_final"] - r.prima_final, 2),
        })
    return sorted(salida, key=lambda x: (-x["ahorro_extra"], -x["puntos"]))


# --- Alta y edición de asegurados desde el panel -----------------------------------

EDAD_MIN, EDAD_MAX = 18, 90
PRIMA_MIN, PRIMA_MAX = 10.0, 2000.0


def siguiente_poliza(asegurados: list[dict]) -> str:
    """Siguiente número de póliza libre: POL-0016 si la mayor es POL-0015."""
    numeros = [int(a["poliza"].split("-")[-1]) for a in asegurados if str(a.get("poliza", "")).split("-")[-1].isdigit()]
    return f"POL-{max(numeros, default=0) + 1:04d}"


def validar_datos(nombre: str, edad: int, prima: float) -> list[str]:
    """Problemas con los datos de un asegurado, en lenguaje claro. Lista vacía si todo está bien."""
    problemas = []
    if not str(nombre).strip():
        problemas.append("Escriba el nombre del asegurado.")
    if not EDAD_MIN <= int(edad) <= EDAD_MAX:
        problemas.append(f"La edad debe estar entre {EDAD_MIN} y {EDAD_MAX} años.")
    if not PRIMA_MIN <= float(prima) <= PRIMA_MAX:
        problemas.append(f"La prima debe estar entre ${PRIMA_MIN:.0f} y ${PRIMA_MAX:.0f} al mes.")
    return problemas


def prima_con_descuento(asegurado: dict, nueva_prima_base: float) -> float:
    """Prima final al cambiar la prima base: se conserva el descuento del nivel que ya ganó."""
    return prima_final(nueva_prima_base, int(asegurado.get("descuento", 0)))
