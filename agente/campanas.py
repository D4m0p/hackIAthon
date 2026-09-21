"""Paso 2: diseño de campañas de prevención con IA (Groq), con respaldo por plantillas.

El modelo solo recibe el resumen agregado de `analisis.resumen_para_ia`.
Todo lo que devuelve se valida antes de llegar al CRM.
"""

import json

import requests

from agente.catalogo import CHEQUEOS, NOMBRES_CAMPANA, POBLACION_BASE, SEXO_OBLIGATORIO

URL_GROQ = "https://api.groq.com/openai/v1/chat/completions"
MODELO_POR_DEFECTO = "llama-3.3-70b-versatile"

INSTRUCCIONES = f"""Eres el agente de bienestar preventivo de una aseguradora de salud en Latinoamérica.
Recibes estadísticas ANÓNIMAS y agregadas de los diagnósticos más frecuentes del hospital.
Diseña UNA campaña de prevención por cada diagnóstico recibido.

Reglas:
- "tipo_chequeo" debe ser exactamente el "chequeo_preventivo" del diagnóstico. Códigos válidos: {", ".join(CHEQUEOS)}.
- Define la población objetivo (sexo "M", "F" o "Todos"; edad_min y edad_max) según las guías clínicas
  y los grupos más afectados que ves en los datos.
- "puntos": entre 50 y 150. Da más puntos a los chequeos que detectan enfermedades más graves o menos
  realizadas por la población.
- "mensaje": máximo 280 caracteres, cálido y motivador, en español neutro y tratando de "usted".
  Menciona el beneficio (puntos que bajan su prima). No prometas diagnósticos ni curas.
- "justificacion": una frase que explique qué dato del análisis motiva la campaña.

Responde SOLO con JSON de esta forma:
{{"campanas": [{{"nombre": "...", "tipo_chequeo": "...", "diagnostico": "...", "sexo": "...",
"edad_min": 0, "edad_max": 0, "puntos": 0, "mensaje": "...", "justificacion": "..."}}]}}"""


def _plantilla(item: dict) -> dict:
    tipo = item["chequeo_preventivo"]
    base = POBLACION_BASE[tipo]
    return {
        "nombre": NOMBRES_CAMPANA[tipo],
        "tipo_chequeo": tipo,
        "diagnostico": item["diagnostico"],
        **base,
        "puntos": 150 if tipo in SEXO_OBLIGATORIO or tipo == "COLONOSCOPIA" else 100,
        "mensaje": (
            f"Cuide su salud: realícese su {CHEQUEOS[tipo].lower()} en nuestro hospital "
            "y gane puntos que reducen su prima. La detección temprana salva vidas."
        ),
        "justificacion": f"{item['diagnostico']} representa el {item['porcentaje_del_total']} % de los diagnósticos.",
    }


def _validar(c: dict, item: dict) -> dict:
    """Corrige lo que la IA haya propuesto fuera de rango. Nunca confía a ciegas."""
    tipo = item["chequeo_preventivo"]
    base = POBLACION_BASE[tipo]
    sexo = SEXO_OBLIGATORIO.get(tipo) or (c.get("sexo") if c.get("sexo") in ("M", "F", "Todos") else base["sexo"])
    try:
        edad_min = max(18, min(int(c["edad_min"]), 90))
        edad_max = max(edad_min, min(int(c["edad_max"]), 90))
    except (KeyError, TypeError, ValueError):
        edad_min, edad_max = base["edad_min"], base["edad_max"]
    try:
        puntos = max(50, min(int(c["puntos"]), 150))
    except (KeyError, TypeError, ValueError):
        puntos = 100
    return {
        "nombre": str(c.get("nombre") or NOMBRES_CAMPANA[tipo])[:100],
        "tipo_chequeo": tipo,
        "diagnostico": item["diagnostico"],
        "sexo": sexo,
        "edad_min": edad_min,
        "edad_max": edad_max,
        "puntos": puntos,
        "mensaje": str(c.get("mensaje") or _plantilla(item)["mensaje"])[:400],
        "justificacion": str(c.get("justificacion") or "")[:300],
    }


def disenar(resumen: list[dict], api_key: str | None, modelo: str | None = None) -> tuple[list[dict], str]:
    """Devuelve (campañas, origen). Origen: 'ia' o 'plantillas' (con el motivo)."""
    if not api_key:
        return [_plantilla(i) for i in resumen], "plantillas (sin clave de Groq configurada)"
    try:
        r = requests.post(
            URL_GROQ,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": modelo or MODELO_POR_DEFECTO,
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": INSTRUCCIONES},
                    {"role": "user", "content": json.dumps(resumen, ensure_ascii=False)},
                ],
            },
            timeout=30,
        )
        r.raise_for_status()
        propuestas = json.loads(r.json()["choices"][0]["message"]["content"])["campanas"]
    except Exception as e:  # la demo nunca debe caerse por la IA
        return [_plantilla(i) for i in resumen], f"plantillas (la IA falló: {type(e).__name__})"

    por_tipo = {p.get("tipo_chequeo"): p for p in propuestas if isinstance(p, dict)}
    campanas = [
        _validar(por_tipo[i["chequeo_preventivo"]], i) if i["chequeo_preventivo"] in por_tipo else _plantilla(i)
        for i in resumen
    ]
    return campanas, "ia"
