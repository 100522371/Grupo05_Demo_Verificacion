# Demo · ¿Qué detecta cada capa de verificación?

Caso común del seminario *«¿Podemos fiarnos del código que genera la IA?»*
(IAO 2026/27, grupo 5). El mismo módulo, generado «por un asistente», se pasa por
siete capas de verificación y se construye una matriz **defecto × capa**.

## Ejecutarlo

```bash
pip install -r requirements-dev.txt          # pytest y ruff
python herramientas/ejecutar_demo.py --version generado     # código tal cual
python herramientas/ejecutar_demo.py --version corregido    # código tras corregirlo
python herramientas/comprobar_dependencias.py caso/requirements_caso_real.txt
```

Requisitos: CPython 3.10 o superior. Con `--online` la comprobación de dependencias
consulta PyPI en ese momento; sin él usa la foto del 22/11/2026
(`herramientas/snapshot_pypi_2026-11-22.json`).

## Qué contiene

| Ruta | Contenido |
| --- | --- |
| `caso/prompt_original.md` | Prompt, escenario y origen de cada fragmento |
| `caso/pedidos_generado.py` | Código «del asistente», con 6 defectos conocidos |
| `caso/pedidos_corregido.py` | Código tras la verificación |
| `caso/requirements_*.txt` | Dependencias propuestas, corregidas y el caso real `huggingface-cli` |
| `tests/test_base.py` | **L0** · casos típicos (los 4 de HumanEval/58 + 4 más) |
| `tests/test_ampliados.py` | **L1** · casos límite (incluida la entrada de HumanEval+) |
| `tests/test_propiedades.py` | **L2** · propiedades y oráculo diferencial, con reducción de contraejemplos |
| `tests/test_seguridad.py` | **L3** · entradas adversarias |
| `herramientas/ejecutar_demo.py` | Ejecuta todo y genera la matriz en `resultados/` |
| `herramientas/comprobar_dependencias.py` | **L5** · existencia y señales de legitimidad en PyPI |
| `protocolo_comparacion_asistentes.md` | Cómo repetir el experimento con asistentes reales |

**L4** es análisis estático con `ruff --select S,BLE` (las reglas `S` son las de Bandit).
Si `bandit` está instalado, el script también lo ejecuta. **L6** es una lista de control
para la revisión humana: no se automatiza.

## Resultado obtenido (22/11/2026, CPython 3.13, pytest 9.1, ruff 0.16)

| Defecto | L0 | L1 | L2 | L3 | L4 | L5 | L6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D1 · `clientes_comunes` desordenada (fallo real de EvalPlus) | ✘ | ✔ | ✔ | ✘ | ✘ | ✘ | ☐ |
| D2a · errores ocultos / apóstrofos (CWE-390) | ✘ | ✔ | ✔ | ✘ | ✔ | ✘ | ☐ |
| D2b · inyección SQL (CWE-89) | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ | ☐ |
| D3 · token predecible (CWE-330) | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ | ☐ |
| D4 · paquete inexistente | ✘ | ✘ | ✘ | ✘ | ✘ | ✔ | ☐ |
| D5 · falta autorización (CWE-862) | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ☐ |

✔ detectado · ✘ no detectado · ☐ depende de quien revise

Evidencias concretas de esa ejecución:

- **L0**: 8/8 tests superados. El código «funciona».
- **L1**: `clientes_comunes([6, 8, 1], [6, 8, 1])` devuelve `[8, 1, 6]`;
  `"O'Brien"` devuelve `[]` en vez de su pedido; una BD sin tabla devuelve `[]` en vez de error.
- **L2**: contraejemplo reducido `([1, 8], [8, 1])` → `[8, 1]`; el nombre aleatorio `'jzPde`
  falla en el primer intento.
- **L3**: `"x' OR '1'='1"` devuelve los 5 pedidos de la tabla; con la misma semilla de `random`
  se obtiene el mismo token.
- **L4**: `S608` (SQL con cadenas, línea 24), `BLE001` (`except Exception`, línea 27),
  `S311` (`random` para un secreto, línea 34).
- **L5**: `sqlite-injection-guard` no existe → BLOQUEAR. En el caso real, `huggingface-cli`
  sí existe (alguien registró el nombre alucinado) → REVISAR. Que exista no basta.
- **Versión corregida**: 23/23 tests, 0 hallazgos y dependencias OK. D5 sigue pendiente:
  es una decisión de diseño que ninguna herramienta toma por nosotros.

La matriz y las evidencias están en `resultados/`.

## Condiciones y límites

- Los defectos se conocen de antemano. Solo `clientes_comunes` reproduce una salida real
  publicada (Liu et al., 2023); el resto son patrones documentados escritos para la clase.
  La demo enseña **qué tipo de problema ve cada capa**. No mide la frecuencia de esos
  problemas en ningún asistente.
- El fallo D1 depende del orden de iteración de los `set` de CPython (detalle de implementación).
- Los resultados de L4 dependen de la herramienta y de su configuración. Por ejemplo, el
  catálogo de Bandit no incluye una regla para `except Exception` como `BLE001` de ruff.
  Si usáis Bandit, anotad qué reglas saltan en vuestra ejecución.
- La comprobación de dependencias es una foto: un nombre que hoy no existe puede registrarlo
  mañana cualquiera. Por eso se comprueba en cada instalación, en la integración continua.
- Datos 100 % sintéticos. No se ha introducido código ni información de terceros en ninguna herramienta.
