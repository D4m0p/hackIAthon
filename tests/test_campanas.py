from agente.campanas import _validar, disenar

ITEM = {"diagnostico": "Tumor maligno de próstata", "codigo_cie10": "C61", "casos": 48,
        "porcentaje_del_total": 2.7, "chequeo_preventivo": "PROSTATA", "grupos_mas_afectados": []}


def test_sin_clave_usa_plantillas():
    campanas, origen = disenar([ITEM], api_key=None)
    assert origen.startswith("plantillas")
    assert campanas[0]["tipo_chequeo"] == "PROSTATA" and campanas[0]["sexo"] == "M"


def test_validar_corrige_propuestas_sin_sentido():
    c = _validar({"sexo": "F", "edad_min": 5, "edad_max": 300, "puntos": 9999, "nombre": "X"}, ITEM)
    assert c["sexo"] == "M"  # próstata siempre es para hombres
    assert (c["edad_min"], c["edad_max"], c["puntos"]) == (18, 90, 150)


def test_validar_tolera_campos_basura():
    c = _validar({"edad_min": "abc", "puntos": None}, ITEM)
    assert (c["edad_min"], c["edad_max"], c["puntos"]) == (45, 75, 100)
