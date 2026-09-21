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


class _Resp:
    def __init__(self, status):
        self.status_code = status


def test_respaldo_si_el_modelo_principal_agota_su_cupo(monkeypatch):
    import requests
    from agente import campanas
    usados = []

    def falso(resumen, key, modelo):
        usados.append(modelo)
        if modelo == campanas.MODELO_POR_DEFECTO:
            raise requests.HTTPError(response=_Resp(429))
        return [{"tipo_chequeo": "PROSTATA", "nombre": "Desde respaldo", "sexo": "M",
                 "edad_min": 50, "edad_max": 70, "puntos": 120, "mensaje": "Hola"}]

    monkeypatch.setattr(campanas, "_pedir_a_groq", falso)
    cs, origen = campanas.disenar([ITEM], api_key="x")
    assert usados == [campanas.MODELO_POR_DEFECTO, campanas.MODELO_RESPALDO]
    assert origen == "ia" and cs[0]["nombre"] == "Desde respaldo"


def test_plantillas_si_ningun_modelo_responde(monkeypatch):
    import requests
    from agente import campanas

    def falso(*_):
        raise requests.HTTPError(response=_Resp(429))

    monkeypatch.setattr(campanas, "_pedir_a_groq", falso)
    cs, origen = campanas.disenar([ITEM], api_key="x")
    assert origen == "plantillas (la IA no respondió: cupo de Groq agotado por este minuto)"
    assert cs[0]["tipo_chequeo"] == "PROSTATA"
