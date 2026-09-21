"""Catálogo de chequeos preventivos (sección 4 del contrato)."""

CHEQUEOS = {
    "PROSTATA": "Antígeno prostático (PSA)",
    "MAMOGRAFIA": "Mamografía",
    "PAPANICOLAOU": "Papanicolaou",
    "GLUCOSA": "Glucosa en ayunas / HbA1c",
    "PRESION": "Control de presión arterial",
    "COLESTEROL": "Perfil lipídico",
    "COLONOSCOPIA": "Colonoscopía / sangre oculta",
}

# Nombres de campaña para cuando no hay IA disponible.
NOMBRES_CAMPANA = {
    "PROSTATA": "Hombres que se chequean a tiempo",
    "MAMOGRAFIA": "Mamografía a tiempo",
    "PAPANICOLAOU": "Un Papanicolaou al año",
    "GLUCOSA": "Glucosa bajo control",
    "PRESION": "Presión en su punto",
    "COLESTEROL": "Corazón sin colesterol",
    "COLONOSCOPIA": "Colon sano después de los 45",
}

# Prefijo CIE-10 del diagnóstico -> chequeo que lo previene o detecta a tiempo.
CIE10_A_CHEQUEO = {
    "C61": "PROSTATA",
    "C50": "MAMOGRAFIA",
    "C53": "PAPANICOLAOU",
    "E11": "GLUCOSA",
    "I10": "PRESION",
    "E78": "COLESTEROL",
    "C18": "COLONOSCOPIA",
}

# Población objetivo según guías clínicas habituales. También sirve para
# corregir a la IA si propone una población sin sentido médico.
POBLACION_BASE = {
    "PROSTATA": {"sexo": "M", "edad_min": 45, "edad_max": 75},
    "MAMOGRAFIA": {"sexo": "F", "edad_min": 40, "edad_max": 74},
    "PAPANICOLAOU": {"sexo": "F", "edad_min": 25, "edad_max": 64},
    "GLUCOSA": {"sexo": "Todos", "edad_min": 35, "edad_max": 75},
    "PRESION": {"sexo": "Todos", "edad_min": 18, "edad_max": 90},
    "COLESTEROL": {"sexo": "Todos", "edad_min": 40, "edad_max": 75},
    "COLONOSCOPIA": {"sexo": "Todos", "edad_min": 45, "edad_max": 75},
}

# Chequeos que solo aplican a un sexo, sin importar lo que proponga la IA.
SEXO_OBLIGATORIO = {"PROSTATA": "M", "MAMOGRAFIA": "F", "PAPANICOLAOU": "F"}


def chequeo_para_cie10(codigo: str) -> str | None:
    return CIE10_A_CHEQUEO.get(str(codigo)[:3].upper())
