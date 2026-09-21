# Tareas pendientes del equipo

Demo pública: <https://bienestar-preventivo.streamlit.app/>

Las reglas de trabajo siguen siendo las de [`CONTRATO.md`](CONTRATO.md) (lea la sección 0 antes de hacer cualquier commit).

---

## Persona 3: revisión de la IA y prueba final

La clave de Groq ya está conectada. Estado del modelo:

- `llama-3.3-70b-versatile` **ya no existe** en Groq; se reemplazó.
- Modelo principal: `openai/gpt-oss-120b`. Si agota su cupo por minuto, el agente usa `qwen/qwen3.8-27b`, y si ninguno responde, usa campañas de plantilla. La demo no se cae.

### 1. Revisión médica de las campañas
En la demo, pestaña **Campañas** → **Diseñar campañas con IA**. Hágalo 3 o 4 veces (la IA varía un poco cada vez) y revise:

- ¿Las edades de cada población objetivo tienen sentido clínico?
  **Caso ya detectado:** la IA suele proponer la campaña de **hipertensión solo para 40–59 años**, dejando fuera a mayores de 60, que son el grupo de más riesgo. ¿Es aceptable o hay que corregirlo?
- ¿Los puntos (50 a 150) están bien repartidos según la gravedad de cada enfermedad?
- ¿Los mensajes son correctos, en español neutro, tratando de "usted" y sin prometer diagnósticos ni curas?

Anote lo que deba corregirse y pásela a la Persona 1. Se puede agregar una regla en el código que corrija automáticamente lo que la IA proponga mal.

### 2. Límite del plan gratuito de Groq
En <https://console.groq.com/settings/limits> confirme los límites de `openai/gpt-oss-120b`.
Con lo medido hoy alcanza para unas **3 tandas de campañas por minuto**. Si el límite es menor, avise.

### 3. Prueba final como jurado
Abra la demo en una ventana privada y haga el recorrido completo:

1. **Análisis anónimo:** ¿se entiende el gráfico y la nota de privacidad?
2. **Campañas:** diseñar → publicar.
3. **Chequeos y premios:** procesar → deben salir 5 premiados y 3 rechazados con su motivo.
4. Simule un chequeo nuevo y procéselo.
5. **CRM de asegurados:** ¿se ven los puntos, niveles y primas actualizados?
6. Pruebe también desde el celular.

Anote cualquier error o cosa confusa y pásela a la Persona 1.

### 4. Correo de entrega
Prepare el borrador para **hackiathon@viamatica.com** con:

- Enlace público del agente: <https://bienestar-preventivo.streamlit.app/>
- Enlace del repositorio: <https://github.com/D4m0p/hackIAthon>

No lo envíe hasta que el equipo confirme que todo está listo.

---

## Persona 2: CRM en Notion

Pendiente: crear las bases según la sección 2 de [`CONTRATO.md`](CONTRATO.md) y enviar **por privado** a la Persona 1 el token, los 3 IDs de las bases y el enlace público de la página.
