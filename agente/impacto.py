"""Impacto económico para la aseguradora.

Cifras REFERENCIALES para la demostración: el panel permite editarlas en vivo.
"""

import pandas as pd

from agente.catalogo import CHEQUEOS, POBLACION_BASE

# tipo: (costo del chequeo USD, % de chequeos con hallazgo temprano, costo evitado por caso detectado a tiempo USD)
SUPUESTOS = {
    "PRESION": (5, 10.0, 1500),
    "GLUCOSA": (8, 6.0, 2500),
    "COLESTEROL": (15, 12.0, 1200),
    "PROSTATA": (30, 2.0, 18000),
    "MAMOGRAFIA": (70, 0.6, 22000),
    "PAPANICOLAOU": (25, 0.4, 12000),
    "COLONOSCOPIA": (150, 1.0, 20000),
}


def supuestos_tabla(tipos: list[str]) -> pd.DataFrame:
    return pd.DataFrame([
        {"tipo": t, "Chequeo": CHEQUEOS[t], "Costo del chequeo ($)": SUPUESTOS[t][0],
         "Hallazgo temprano (%)": SUPUESTOS[t][1], "Costo evitado por caso ($)": SUPUESTOS[t][2]}
        for t in tipos
    ])


def fraccion_elegible(poblacion: pd.DataFrame, campana: dict) -> float:
    """Qué parte de la población (según sexo y edad del hospital) entra en la campaña."""
    base = POBLACION_BASE.get(campana["tipo_chequeo"], {})
    sexo = campana.get("sexo", base.get("sexo", "Todos"))
    m = poblacion["edad"].between(campana["edad_min"], campana["edad_max"])
    if sexo in ("M", "F"):
        m &= poblacion["sexo"] == sexo
    return float(m.mean()) if len(poblacion) else 0.0


def calcular(poblacion: pd.DataFrame, campanas: list[dict], supuestos: pd.DataFrame,
             asegurados: int, participacion: float, prima_promedio: float, descuento_promedio: float) -> dict:
    """Ahorro anual estimado de la aseguradora, por campaña y en total."""
    s = supuestos.set_index("tipo")
    filas = []
    for c in campanas:
        t = c["tipo_chequeo"]
        if t not in s.index:
            continue
        participantes = asegurados * fraccion_elegible(poblacion, c) * participacion
        casos = participantes * s.at[t, "Hallazgo temprano (%)"] / 100
        filas.append({
            "Campaña": c["nombre"], "tipo": t, "Participantes": round(participantes),
            "Casos detectados a tiempo": round(casos, 1),
            "Ahorro en tratamientos": casos * s.at[t, "Costo evitado por caso ($)"],
            "Costo de los chequeos": participantes * s.at[t, "Costo del chequeo ($)"],
        })
    detalle = pd.DataFrame(filas)
    if detalle.empty:
        return {"detalle": detalle, "ahorro": 0, "chequeos": 0, "descuentos": 0, "neto": 0, "roi": 0, "casos": 0, "personas": 0}
    # Cada persona cuenta una vez para el descuento, aunque participe en varias campañas.
    personas = min(asegurados, detalle["Participantes"].max() * 1.3)
    descuentos = personas * prima_promedio * descuento_promedio / 100 * 12
    ahorro, chequeos = detalle["Ahorro en tratamientos"].sum(), detalle["Costo de los chequeos"].sum()
    costo = chequeos + descuentos
    return {
        "detalle": detalle, "ahorro": ahorro, "chequeos": chequeos, "descuentos": descuentos,
        "neto": ahorro - costo, "roi": ahorro / costo if costo else 0,
        "casos": detalle["Casos detectados a tiempo"].sum(), "personas": round(personas),
    }
