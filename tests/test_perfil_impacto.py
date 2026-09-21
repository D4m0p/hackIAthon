import pandas as pd

from agente import impacto
from agente.perfil import insignias, recomendaciones

LUCIA = {"nombre": "Lucía", "sexo": "F", "edad": 47, "prima_base": 120.0, "puntos": 150, "prima_final": 114.0}
MAMO = {"nombre": "Mamografía", "tipo_chequeo": "MAMOGRAFIA", "sexo": "F", "edad_min": 40, "edad_max": 74, "puntos": 100, "estado": "Activa"}
PSA = {"nombre": "Próstata", "tipo_chequeo": "PROSTATA", "sexo": "M", "edad_min": 45, "edad_max": 75, "puntos": 150, "estado": "Activa"}
COL = {"nombre": "Colesterol", "tipo_chequeo": "COLESTEROL", "sexo": "Todos", "edad_min": 40, "edad_max": 75, "puntos": 50, "estado": "Activa"}


def test_insignias():
    ganadas = {i["clave"] for i in insignias(LUCIA, ["MAMOGRAFIA", "COLESTEROL"]) if i["ganada"]}
    assert ganadas == {"primer", "temprana", "corazon", "constancia", "plata"}


def test_recomendaciones_filtra_y_ordena():
    recs = recomendaciones(LUCIA, [PSA, MAMO, COL], tipos_cumplidos=["COLESTEROL"])
    assert [r["campana"]["tipo_chequeo"] for r in recs] == ["MAMOGRAFIA"]  # próstata no aplica, colesterol ya hecho
    assert recs[0]["sube"] and recs[0]["nivel_nuevo"] == "Oro" and recs[0]["ahorro_extra"] == 6.0


def test_impacto_positivo_y_coherente():
    pob = pd.DataFrame({"edad": [30, 45, 50, 60, 70], "sexo": ["F", "F", "M", "F", "M"]})
    assert impacto.fraccion_elegible(pob, MAMO) == 0.4  # mujeres de 45 y 60
    r = impacto.calcular(pob, [MAMO, PSA], impacto.supuestos_tabla(["MAMOGRAFIA", "PROSTATA"]),
                         asegurados=10000, participacion=0.3, prima_promedio=130, descuento_promedio=5)
    assert r["neto"] == r["ahorro"] - r["chequeos"] - r["descuentos"]
    assert set(r["detalle"]["tipo"]) == {"MAMOGRAFIA", "PROSTATA"}
    assert r["personas"] <= 10000
