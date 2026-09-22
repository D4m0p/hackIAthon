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


def test_validar_no_deja_fuera_a_los_mayores():
    presion = {"diagnostico": "Hipertensión esencial", "codigo_cie10": "I10", "casos": 255,
               "porcentaje_del_total": 14.2, "chequeo_preventivo": "PRESION", "grupos_mas_afectados": []}
    c = _validar({"sexo": "Todos", "edad_min": 40, "edad_max": 59, "puntos": 120, "justificacion": "Pico en 40-59."}, presion)
    assert (c["edad_min"], c["edad_max"]) == (40, 90)  # conserva el foco, pero incluye a los mayores de 60
    assert "ampliado por reglas clínicas de 59 a 90" in c["justificacion"]
    # Si la IA ya incluye a los mayores, no se toca nada.
    c = _validar({"edad_min": 40, "edad_max": 90, "puntos": 100}, presion)
    assert c["edad_max"] == 90 and "ampliado" not in c["justificacion"]


def test_diego_de_67_ya_no_queda_fuera():
    from agente.premios import evaluar
    presion = {"diagnostico": "Hipertensión esencial", "porcentaje_del_total": 14.2, "chequeo_preventivo": "PRESION"}
    campana = {**_validar({"sexo": "Todos", "edad_min": 40, "edad_max": 59, "puntos": 120}, presion), "id": "c1", "estado": "Activa"}
    diego = {"id": "a7", "poliza": "POL-0007", "nombre": "Diego Castillo", "sexo": "M", "edad": 67,
             "prima_base": 175.0, "puntos": 0, "nivel": "Bronce", "descuento": 0, "prima_final": 175.0}
    decisiones, _ = evaluar([{"id_chequeo": "CHQ-1008", "poliza": "POL-0007", "tipo_chequeo": "PRESION", "fecha": "2026-09-11"}],
                            [diego], [campana], set())
    assert decisiones[0].estado == "Premiado"
