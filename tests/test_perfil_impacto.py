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


def test_matriz_riesgo_suprime_grupos_pequenos():
    from agente.analisis import MINIMO_POR_GRUPO, cargar, matriz_riesgo
    m = matriz_riesgo(cargar("data/diagnosticos.csv"))
    assert m.loc[m["suprimido"], "casos"].isna().all()
    assert (m.loc[~m["suprimido"], "casos"] >= MINIMO_POR_GRUPO).all()
    assert not ((m["diagnostico"] == "Tumor maligno de próstata") & (m["sexo"] == "Mujeres")).any()
    assert "Infección respiratoria aguda" not in set(m["diagnostico"])  # solo prevenibles


def test_contador_grande_elige_formato_y_no_parte_de_cero():
    from agente.ui import _cuenta_grande
    assert 'class="v-cnt-g g2"' in _cuenta_grande(804_135) and "--hasta:804135" in _cuenta_grande(804_135)
    assert 'class="v-cnt-g g3"' in _cuenta_grande(1_250_000)
    assert "--desde:1000;" in _cuenta_grande(1_500)  # nunca arranca con menos cifras que el valor final
    assert _cuenta_grande(-2_000).startswith("−")


def test_alta_y_edicion_de_asegurados():
    from agente.crm import CRMLocal
    from agente.perfil import prima_con_descuento, siguiente_poliza, validar_datos
    crm = CRMLocal()
    crm.reiniciar([{"poliza": "POL-0015", "nombre": "Ana", "sexo": "F", "edad": 40, "prima_base": 100.0}])
    assert siguiente_poliza(crm.asegurados()) == "POL-0016"
    assert siguiente_poliza([]) == "POL-0001"
    assert validar_datos("", 10, 5) == ["Escriba el nombre del asegurado.", "La edad debe estar entre 18 y 90 años.",
                                        "La prima debe estar entre $10 y $2000 al mes."]
    assert validar_datos("Luis", 50, 120) == []
    crm.crear_asegurado({"poliza": "POL-0016", "nombre": "Luis", "sexo": "M", "edad": 50, "prima_base": 120.0})
    assert [a["poliza"] for a in crm.asegurados()] == ["POL-0015", "POL-0016"]
    # Editar conserva el descuento ganado: con 5 % (Plata), una prima base de 200 queda en 190.
    ana = crm.asegurados()[0] | {"descuento": 5}
    crm.editar_asegurado(ana["id"], 41, 200.0, prima_con_descuento(ana, 200.0))
    ana = crm.asegurados()[0]
    assert (ana["edad"], ana["prima_base"], ana["prima_final"]) == (41, 200.0, 190.0)
