# Protocolo para comparar asistentes reales con el mismo caso

El módulo `caso/pedidos_generado.py` es un **ejemplo controlado**: sabemos de antemano
qué defectos tiene, así que podemos comprobar qué capa detecta cada uno. Si queréis
añadir una comparación entre asistentes reales (Copilot, ChatGPT, Claude, Gemini…),
seguid este protocolo para que el resultado sea defendible en la exposición.

## 1. Condiciones (anotadlas todas)

| Campo | Ejemplo |
| --- | --- |
| Asistente y modo | GitHub Copilot Chat (modo chat), ChatGPT (web), Claude (web) |
| Modelo y versión | El que muestre la herramienta el día de la prueba |
| Fecha y hora | 2026-11-25 10:30 |
| Ajustes | Sesión nueva, sin instrucciones personalizadas ni memoria, sin adjuntos |
| Prompt | Exactamente el de `caso/prompt_original.md`, sin retoques |
| Repeticiones | 3 por asistente (los modelos no son deterministas) |

## 2. Procedimiento

1. Pegad el prompt en una conversación nueva.
2. Guardad el código tal cual en `caso/pedidos_<asistente>_<n>.py` (ej. `pedidos_chatgpt_1.py`)
   y el requirements en `caso/requirements_<asistente>_<n>.txt`. **No instaléis nada.**
3. Si los nombres de las funciones no coinciden, cread un adaptador mínimo que solo
   renombre (sin tocar la lógica) y anotadlo.
4. Ejecutad `python herramientas/ejecutar_demo.py --version <asistente>_<n> --online`.
5. Copiad la fila del resumen en `plantilla_resultados.csv` y guardad la carpeta `resultados/`.
6. Cronometrad cuánto tardáis en revisar el código con la lista L6 (minutos).

## 3. Qué podéis concluir y qué no

- **Sí**: «con este prompt, en esta fecha, estas capas detectaron estos problemas».
- **No**: «el asistente X es más seguro que el Y». Tres repeticiones de un prompt no son
  una muestra representativa; los resultados cambian con la versión del modelo y con el
  prompt (Ouyang et al., 2025, sobre no determinismo; Veracode, 2025–2026, para una
  comparación a gran escala).
- Si un asistente acierta en todo, también es un resultado: explicad qué capas lo
  confirmaron y qué sigue sin poder comprobarse automáticamente (D5).

## 4. Datos

Usad solo los datos sintéticos de la demo. No peguéis código ni datos reales de terceros
en herramientas externas (normas de la asignatura, apartado 05).
