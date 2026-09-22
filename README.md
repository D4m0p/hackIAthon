# Agente de Bienestar Preventivo y Gamificación de Salud

Agente que analiza de forma **anónima** los diagnósticos más frecuentes del hospital,
diseña campañas de prevención con IA y, cuando el asegurado cumple su chequeo,
le otorga **puntos, nivel y descuento en la prima** de forma automática en el CRM de Notion.

- **Demo pública:** <https://bienestar-preventivo.streamlit.app/>
- **CRM en Notion (solo lectura):** <https://luminous-conifer-53c.notion.site/CRM-Aseguradora-Bienestar-Preventivo-3e2cc66afc378176b55ad1f76376368a>

> Todos los datos son ficticios y fueron generados para esta demostración.

## Cómo probarlo en un minuto

1. Abra la demo y presione **Ejecutar el agente completo**. El agente recorre solo todo el ciclo:
   analiza los diagnósticos, diseña las campañas con IA, las publica en el CRM, verifica los
   chequeos del hospital y premia a quien cumplió.
2. Recorra las pestañas para ver el detalle de cada paso.
3. Abra el CRM en Notion y compruebe que los puntos, niveles y primas quedaron actualizados.

Si la página tarda en abrir, el servidor gratuito se está reactivando: basta con esperar unos segundos.

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

| Paso | Qué hace |
|---|---|
| **1. Analizar** | Cuenta los diagnósticos, los agrupa por sexo y rango de edad, y oculta los grupos con menos de 5 casos. Un mapa de riesgo muestra dónde se concentra cada enfermedad prevenible. |
| **2. Diseñar** | Envía al modelo **solo el resumen agregado** y recibe una campaña por diagnóstico: población objetivo, puntos y mensaje. Cada propuesta se valida con reglas clínicas antes de publicarse. |
| **3. Premiar** | Verifica que el chequeo pertenezca a una campaña activa y que el asegurado esté en la población objetivo. Suma puntos, sube el nivel y recalcula la prima en Notion. Nunca premia dos veces el mismo chequeo. |

### El agente no confía a ciegas en la IA

Toda propuesta del modelo pasa por una validación antes de llegar al CRM:

- **Sexo obligatorio:** próstata solo para hombres; mamografía y Papanicolaou solo para mujeres.
- **Nadie de mayor riesgo queda fuera:** si la IA termina una campaña antes de la edad que marcan
  las guías clínicas, el agente amplía el rango y lo explica en la justificación.
- **Límites:** edades entre 18 y 90 años y puntos entre 50 y 150.
- **Respaldo:** si el modelo principal agota su cupo, se usa un segundo modelo; si ninguno
  responde, se usan campañas de plantilla. La demo no se cae por la IA.

### Gamificación

| Nivel | Puntos | Descuento en la prima |
|---|---|---|
| Bronce | 0 – 99 | 0 % |
| Plata | 100 – 199 | 5 % |
| Oro | 200 o más | 10 % |

El panel incluye un ranking con podio, el perfil de cada asegurado con su tarjeta de membresía,
insignias y las campañas que el agente le recomienda hacer a continuación.

La página pública del CRM en Notion es de **solo lectura**: los datos cambian únicamente a través
del agente. Desde la pestaña **Asegurados** se puede agregar un asegurado (el agente indica para qué
campañas activas califica) o editar su edad y su prima base. Los puntos, el nivel y el descuento no
se editan a mano: solo se ganan cumpliendo chequeos.

### Impacto económico

Una pestaña estima el ahorro anual de la aseguradora: casos detectados a tiempo, ahorro en
tratamientos, costo de los chequeos y descuentos pagados. El tamaño de la cartera, la participación
y los supuestos por chequeo se pueden editar en vivo. Las cifras son **referenciales** para la demostración.

### Privacidad desde el diseño

- Los diagnósticos llegan **sin nombre ni póliza**; si un archivo trae columnas identificables, se descartan.
- El modelo de IA **solo recibe conteos agregados**, y el panel muestra exactamente qué se le envía.
- Los grupos de sexo y edad con menos de 5 casos se ocultan, también en el mapa de riesgo.
- Solo el paso 3 cruza un chequeo con una póliza, y lo hace dentro del CRM de la aseguradora.

## Tecnología

- **Python** y **Streamlit** para el panel, publicado en Streamlit Community Cloud.
- **Notion API** como CRM: bases `Asegurados`, `Campañas` y `Chequeos`.
- **Groq** para el diseño de campañas: modelo `openai/gpt-oss-120b`, con `qwen/qwen3.8-27b` de respaldo.
- **pandas** y **Altair** para el análisis y los gráficos.

## Estructura

```
app.py                  Panel: pestañas, piloto automático y conexión con los secretos
agente/
  analisis.py           Paso 1: frecuencias, perfiles por grupo y mapa de riesgo (agregados)
  campanas.py           Paso 2: diseño con IA, validación clínica y plantillas de respaldo
  premios.py            Paso 3: verificación de chequeos y cálculo de premios
  gamificacion.py       Reglas de puntos, niveles y descuentos
  perfil.py             Insignias y recomendaciones personales
  impacto.py            Estimación del impacto económico
  crm.py                Cliente de Notion y CRM local en memoria
  catalogo.py           Chequeos preventivos, códigos CIE-10 y poblaciones de referencia
  ui.py                 Estilos y piezas visuales del panel
data/                   Datos ficticios del hospital y de los asegurados
scripts/generar_datos.py  Genera los datos ficticios (semilla fija)
tests/                  Pruebas automáticas
```

## Ejecutar localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml   # complete las claves (opcional)
streamlit run app.py
```

Sin claves, el panel funciona igual: el CRM corre en memoria y las campañas salen de plantillas.

- **Pruebas:** `pip install pytest && python -m pytest`
- **Regenerar los datos ficticios:** `python scripts/generar_datos.py`

### Configuración

Los secretos van en `.streamlit/secrets.toml` (nunca en el repositorio) o en
**Settings → Secrets** de Streamlit Cloud. Vea `.streamlit/secrets.example.toml`.

| Variable | Para qué |
|---|---|
| `NOTION_TOKEN` | Token de la integración de Notion |
| `NOTION_DB_ASEGURADOS`, `NOTION_DB_CAMPANAS`, `NOTION_DB_CHEQUEOS` | IDs de las tres bases |
| `NOTION_URL_PUBLICA` | Opcional: botón "Ver el CRM en Notion" |
| `GROQ_API_KEY` | Clave de Groq |
| `GROQ_MODEL` | Opcional: modelo principal |
