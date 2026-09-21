"""Perfil del asegurado: insignias ganadas y recomendaciones personales del agente."""

from agente.gamificacion import aplica_a, premiar

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
