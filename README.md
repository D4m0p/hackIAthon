# Agente de Bienestar Preventivo y Gamificación de Salud

Agente que analiza de forma **anónima** los diagnósticos más frecuentes del hospital,
diseña campañas de prevención con IA y, cuando el asegurado cumple su chequeo,
le otorga **puntos, nivel y descuento en la prima** de forma automática en el CRM de Notion.

**Demo pública:** <https://bienestar-preventivo.streamlit.app/> · **CRM en Notion (solo lectura):** <https://luminous-conifer-53c.notion.site/CRM-Aseguradora-Bienestar-Preventivo-3e2cc66afc378176b55ad1f76376368a>

> Todos los datos son ficticios y fueron generados para esta demostración.

## Cómo funciona

```
 Hospital (diagnósticos anonimizados)            Hospital (chequeos realizados)
              │                                               │
              ▼                                               ▼
 1. ANALIZAR ──────────► 2. DISEÑAR CAMPAÑAS ──────► 3. VERIFICAR Y PREMIAR
 frecuencias por          IA (Groq) + validación      cruza chequeo ↔ póliza,
 diagnóstico, sexo        con reglas clínicas         suma puntos, sube de nivel,
 y edad (agregado)                │                   baja la prima
                                  ▼                           │
                         ┌────────────────── CRM en Notion ◄──┘
                         │  Asegurados · Campañas · Chequeos
                         └──────────────────────────────────
```

| Paso | Qué hace | Módulo |
|---|---|---|
| 1. Analizar | Cuenta diagnósticos, los agrupa por sexo y rango de edad y suprime los grupos con menos de 5 casos | `agente/analisis.py` |
| 2. Diseñar | Envía **solo el resumen agregado** al modelo, que propone una campaña por diagnóstico. Cada propuesta se valida (población objetivo, puntos, sexo obligatorio). Si la IA falla, usa plantillas | `agente/campanas.py` |
| 3. Premiar | Verifica que el chequeo pertenezca a una campaña activa y que el asegurado esté en la población objetivo. Nunca premia dos veces el mismo chequeo | `agente/premios.py` |
| CRM | Lee y escribe las 3 bases de Notion. Incluye un modo local en memoria por si Notion no está disponible | `agente/crm.py` |

### Gamificación

| Nivel | Puntos | Descuento en la prima |
|---|---|---|
| 🥉 Bronce | 0 – 99 | 0 % |
| 🥈 Plata | 100 – 199 | 5 % |
| 🥇 Oro | 200 o más | 10 % |

### Privacidad desde el diseño

- Los diagnósticos llegan **sin nombre ni póliza**; si un archivo trae columnas identificables, se descartan.
- El modelo de IA **solo recibe conteos agregados**, y el panel muestra exactamente qué se le envía.
- Solo el paso 3 cruza un chequeo con una póliza, y lo hace dentro del CRM de la aseguradora.

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml   # complete las claves (opcional)
streamlit run app.py
```

Sin claves, el panel funciona igual: el CRM corre en memoria y las campañas salen de plantillas.

Pruebas: `pip install pytest && python -m pytest`

Regenerar los datos ficticios: `python scripts/generar_datos.py`

## Equipo

Las instrucciones de trabajo del equipo están en [`CONTRATO.md`](CONTRATO.md). **Léanlo antes de hacer cualquier cambio.**

Las tareas pendientes de cada persona están en [`TAREAS.md`](TAREAS.md).
