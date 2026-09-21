"""Paso 1: análisis anónimo de diagnósticos.

Solo produce datos agregados. Nada de lo que sale de aquí identifica a una persona.
"""

import pandas as pd

from agente.catalogo import chequeo_para_cie10

RANGOS = [18, 30, 40, 50, 60, 70, 120]
ETIQUETAS = ["18-29", "30-39", "40-49", "50-59", "60-69", "70+"]
# Por debajo de este tamaño, un grupo podría identificar a alguien: se suprime.
MINIMO_POR_GRUPO = 5


def cargar(ruta) -> pd.DataFrame:
    df = pd.read_csv(ruta)
    # Defensa: si alguien sube un archivo con columnas identificables, se descartan.
    return df.drop(columns=[c for c in ("nombre", "poliza", "cedula") if c in df.columns])


def frecuencias(df: pd.DataFrame) -> pd.DataFrame:
    """Diagnósticos ordenados por frecuencia, con el chequeo que los previene."""
    tabla = (
        df.groupby(["codigo_cie10", "diagnostico"]).size()
        .reset_index(name="casos")
        .sort_values("casos", ascending=False, ignore_index=True)
    )
    tabla["porcentaje"] = (tabla["casos"] / len(df) * 100).round(1)
    tabla["chequeo_preventivo"] = tabla["codigo_cie10"].map(chequeo_para_cie10)
    return tabla


def perfil_por_grupo(df: pd.DataFrame, codigo_cie10: str) -> pd.DataFrame:
    """Casos de un diagnóstico por sexo y rango de edad (grupos pequeños suprimidos)."""
    sub = df[df["codigo_cie10"] == codigo_cie10].copy()
    sub["rango_edad"] = pd.cut(sub["edad"], bins=RANGOS, labels=ETIQUETAS, right=False)
    g = sub.groupby(["sexo", "rango_edad"], observed=True).size().reset_index(name="casos")
    return g[g["casos"] >= MINIMO_POR_GRUPO].reset_index(drop=True)


def resumen_para_ia(df: pd.DataFrame, top: int = 5) -> list[dict]:
    """Lo único que recibe el modelo de IA: conteos agregados de los diagnósticos prevenibles."""
    prevenibles = frecuencias(df).dropna(subset=["chequeo_preventivo"]).head(top)
    resumen = []
    for fila in prevenibles.itertuples():
        grupos = perfil_por_grupo(df, fila.codigo_cie10)
        resumen.append({
            "diagnostico": fila.diagnostico,
            "codigo_cie10": fila.codigo_cie10,
            "casos": int(fila.casos),
            "porcentaje_del_total": float(fila.porcentaje),
            "chequeo_preventivo": fila.chequeo_preventivo,
            "grupos_mas_afectados": [
                {"sexo": r.sexo, "rango_edad": str(r.rango_edad), "casos": int(r.casos)}
                for r in grupos.sort_values("casos", ascending=False).head(4).itertuples()
            ],
        })
    return resumen
