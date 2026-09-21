"""Reglas de puntos, niveles y descuentos (sección 6 del contrato).

Funciones puras: no tocan Notion ni la red, por eso se prueban solas.
"""

from dataclasses import dataclass

NIVELES = [  # (puntos mínimos, nivel, descuento %)
    (200, "Oro", 10),
    (100, "Plata", 5),
    (0, "Bronce", 0),
]


def nivel_para(puntos: int) -> tuple[str, int]:
    for minimo, nivel, descuento in NIVELES:
        if puntos >= minimo:
            return nivel, descuento
    return "Bronce", 0


def prima_final(prima_base: float, descuento: int) -> float:
    return round(prima_base * (1 - descuento / 100), 2)


def aplica_a(campana: dict, sexo: str, edad: int) -> bool:
    """¿El asegurado está dentro de la población objetivo de la campaña?"""
    if campana.get("estado", "Activa") != "Activa":
        return False
    if campana["sexo"] not in ("Todos", sexo):
        return False
    return campana["edad_min"] <= edad <= campana["edad_max"]


@dataclass
class Resultado:
    puntos: int
    nivel: str
    descuento: int
    prima_final: float
    subio_de_nivel: bool


def premiar(puntos_actuales: int, prima_base: float, puntos_ganados: int) -> Resultado:
    nivel_antes, _ = nivel_para(puntos_actuales)
    puntos = puntos_actuales + puntos_ganados
    nivel, descuento = nivel_para(puntos)
    return Resultado(
        puntos=puntos,
        nivel=nivel,
        descuento=descuento,
        prima_final=prima_final(prima_base, descuento),
        subio_de_nivel=nivel != nivel_antes,
    )
