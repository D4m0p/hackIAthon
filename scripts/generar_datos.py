"""Genera los datos ficticios del hospital (sección 5 del contrato).

Uso:  python scripts/generar_datos.py
Semilla fija: siempre produce los mismos archivos.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
random.seed(2026)

# (código CIE-10, diagnóstico, función de peso según sexo y edad)
DIAGNOSTICOS = [
    ("J06.9", "Infección respiratoria aguda", lambda s, e: 9),
    ("K29.7", "Gastritis", lambda s, e: 5),
    ("M54.5", "Lumbalgia", lambda s, e: 5 if e >= 25 else 2),
    ("I10", "Hipertensión esencial", lambda s, e: 0 if e < 30 else (e - 25) / 4),
    ("E11.9", "Diabetes mellitus tipo 2", lambda s, e: 0 if e < 35 else (e - 30) / 5),
    ("E78.5", "Dislipidemia", lambda s, e: 0 if e < 35 else (e - 30) / 6),
    ("C50.9", "Tumor maligno de mama", lambda s, e: 3.2 if s == "F" and e >= 40 else 0),
    ("C61", "Tumor maligno de próstata", lambda s, e: 6.0 if s == "M" and e >= 50 else 0),
    ("C53.9", "Tumor maligno de cuello uterino", lambda s, e: 1.0 if s == "F" and 30 <= e <= 64 else 0),
    ("C18.9", "Tumor maligno de colon", lambda s, e: 0.9 if e >= 50 else 0),
]


def diagnosticos(n=1800):
    inicio = date(2026, 1, 1)
    filas = []
    for i in range(1, n + 1):
        sexo = random.choice("MF")
        edad = max(18, min(90, int(random.gauss(48, 16))))
        pesos = [max(0, w(sexo, edad)) for _, _, w in DIAGNOSTICOS]
        codigo, nombre, _ = random.choices(DIAGNOSTICOS, weights=pesos)[0]
        fecha = inicio + timedelta(days=random.randint(0, 240))
        filas.append([f"D{i:05d}", edad, sexo, codigo, nombre, fecha.isoformat()])
    return filas


ASEGURADOS = [  # póliza, nombre, sexo, edad, prima base USD
    ("POL-0001", "Carlos Mendoza", "M", 58, 145.00),
    ("POL-0002", "Lucía Paredes", "F", 47, 120.00),
    ("POL-0003", "Andrés Villacís", "M", 32, 85.00),
    ("POL-0004", "María José Andrade", "F", 61, 160.00),
    ("POL-0005", "Jorge Cedeño", "M", 52, 130.00),
    ("POL-0006", "Patricia Salazar", "F", 55, 140.00),
    ("POL-0007", "Diego Castillo", "M", 67, 175.00),
    ("POL-0008", "Gabriela Torres", "F", 29, 80.00),
    ("POL-0009", "Fernando Ruiz", "M", 44, 110.00),
    ("POL-0010", "Verónica Herrera", "F", 38, 95.00),
    ("POL-0011", "Ricardo Espinoza", "M", 71, 190.00),
    ("POL-0012", "Daniela Morán", "F", 50, 125.00),
    ("POL-0013", "Luis Guerrero", "M", 40, 100.00),
    ("POL-0014", "Sofía Benítez", "F", 64, 155.00),
    ("POL-0015", "Martín Zambrano", "M", 49, 115.00),
]

# Lo que el hospital reporta. Incluye casos que el agente debe rechazar.
CHEQUEOS = [
    ("CHQ-1001", "POL-0001", "PROSTATA", "2026-09-02"),
    ("CHQ-1002", "POL-0002", "MAMOGRAFIA", "2026-09-03"),
    ("CHQ-1003", "POL-0002", "COLESTEROL", "2026-09-05"),    # segundo chequeo -> Oro
    ("CHQ-1004", "POL-0003", "PROSTATA", "2026-09-06"),      # 32 años: fuera de población
    ("CHQ-1005", "POL-0005", "GLUCOSA", "2026-09-08"),
    ("CHQ-1006", "POL-0006", "COLONOSCOPIA", "2026-09-09"),  # sin campaña activa (si no entra al top)
    ("CHQ-1007", "POL-0099", "PRESION", "2026-09-10"),       # póliza inexistente
    ("CHQ-1008", "POL-0007", "PRESION", "2026-09-11"),
]


def escribir(nombre, encabezado, filas):
    with open(DATA / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(encabezado)
        w.writerows(filas)
    print(f"{nombre}: {len(filas)} filas")


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    escribir("diagnosticos.csv", ["id_registro", "edad", "sexo", "codigo_cie10", "diagnostico", "fecha"], diagnosticos())
    escribir("asegurados.csv", ["poliza", "nombre", "sexo", "edad", "prima_base"], ASEGURADOS)
    escribir("chequeos.csv", ["id_chequeo", "poliza", "tipo_chequeo", "fecha"], CHEQUEOS)
