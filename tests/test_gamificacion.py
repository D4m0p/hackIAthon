from agente.gamificacion import aplica_a, nivel_para, premiar, prima_final


def test_limites_de_nivel():
    assert nivel_para(0) == ("Bronce", 0)
    assert nivel_para(99) == ("Bronce", 0)
    assert nivel_para(100) == ("Plata", 5)
    assert nivel_para(199) == ("Plata", 5)
    assert nivel_para(200) == ("Oro", 10)
    assert nivel_para(950) == ("Oro", 10)


def test_prima_final():
    assert prima_final(120.0, 0) == 120.0
    assert prima_final(120.0, 5) == 114.0
    assert prima_final(99.99, 10) == 89.99


def test_premiar_sube_de_nivel():
    r = premiar(puntos_actuales=50, prima_base=100.0, puntos_ganados=100)
    assert (r.puntos, r.nivel, r.descuento, r.prima_final) == (150, "Plata", 5, 95.0)
    assert r.subio_de_nivel


def test_premiar_sin_cambio_de_nivel():
    r = premiar(puntos_actuales=100, prima_base=100.0, puntos_ganados=50)
    assert r.nivel == "Plata" and not r.subio_de_nivel


CAMPANA = {"sexo": "M", "edad_min": 45, "edad_max": 75, "estado": "Activa"}


def test_aplica_a_poblacion_objetivo():
    assert aplica_a(CAMPANA, "M", 45)
    assert aplica_a(CAMPANA, "M", 75)
    assert not aplica_a(CAMPANA, "M", 44)
    assert not aplica_a(CAMPANA, "F", 50)
    assert not aplica_a({**CAMPANA, "estado": "Cerrada"}, "M", 50)
    assert aplica_a({**CAMPANA, "sexo": "Todos"}, "F", 50)


def test_siguiente_nivel():
    from agente.gamificacion import siguiente_nivel
    assert siguiente_nivel(0) == ("Plata", 100, 0.0)
    assert siguiente_nivel(50) == ("Plata", 50, 0.5)
    assert siguiente_nivel(150) == ("Oro", 50, 0.5)
    assert siguiente_nivel(200) is None
