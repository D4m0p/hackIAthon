import csv
from pathlib import Path

from agente.campanas import _plantilla
from agente.premios import evaluar

DATA = Path(__file__).resolve().parent.parent / "data"


def _asegurados():
    with open(DATA / "asegurados.csv", encoding="utf-8") as f:
        return [{**r, "id": r["poliza"], "edad": int(r["edad"]), "prima_base": float(r["prima_base"]),
                 "puntos": 0, "nivel": "Bronce", "descuento": 0, "prima_final": float(r["prima_base"])}
                for r in csv.DictReader(f)]


def _chequeos():
    with open(DATA / "chequeos.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _campanas(*tipos):
    return [{**_plantilla({"diagnostico": t, "porcentaje_del_total": 1, "chequeo_preventivo": t}), "id": t, "estado": "Activa"}
            for t in tipos]


CAMPANAS = _campanas("PRESION", "GLUCOSA", "COLESTEROL", "PROSTATA", "MAMOGRAFIA")


def test_demo_completa():
    decisiones, finales = evaluar(_chequeos(), _asegurados(), CAMPANAS, set())
    estados = {d.id_chequeo: d.estado for d in decisiones}
    assert estados == {
        "CHQ-1001": "Premiado", "CHQ-1002": "Premiado", "CHQ-1003": "Premiado",
        "CHQ-1004": "Rechazado", "CHQ-1005": "Premiado", "CHQ-1006": "Rechazado",
        "CHQ-1007": "Rechazado", "CHQ-1008": "Premiado",
    }
    # Lucía: mamografía (150) + colesterol (100) = 250 -> Oro, 10 % sobre 120
    assert (finales["POL-0002"]["nivel"], finales["POL-0002"]["prima_final"]) == ("Oro", 108.0)
    # Carlos: próstata (150) -> Plata, 5 % sobre 145
    assert (finales["POL-0001"]["nivel"], finales["POL-0001"]["prima_final"]) == ("Plata", 137.75)


def test_no_premia_dos_veces():
    decisiones, finales = evaluar(_chequeos(), _asegurados(), CAMPANAS, {"CHQ-1001"})
    assert next(d for d in decisiones if d.id_chequeo == "CHQ-1001").estado == "Ya premiado"
    assert finales["POL-0001"]["puntos"] == 0


def test_mismo_id_repetido_en_el_lote():
    ch = _chequeos()[:1] * 2
    decisiones, finales = evaluar(ch, _asegurados(), CAMPANAS, set())
    assert [d.estado for d in decisiones] == ["Premiado", "Ya premiado"]
    assert finales["POL-0001"]["puntos"] == 150
