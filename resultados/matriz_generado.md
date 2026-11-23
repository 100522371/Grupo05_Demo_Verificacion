# Matriz de detección · versión `generado`

| Defecto | L0 Tests base | L1 Tests ampliados | L2 Propiedades | L3 Tests seguridad | L4 Análisis estático | L5 Dependencias | L6 Revisión humana |
|---|---|---|---|---|---|---|---|
| D1 | ✘ | ✔ | ✔ | ✘ | ✘ | ✘ | ☐ |
| D2a | ✘ | ✔ | ✔ | ✘ | ✔ | ✘ | ☐ |
| D2b | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ | ☐ |
| D3 | ✘ | ✘ | ✘ | ✔ | ✔ | ✘ | ☐ |
| D4 | ✘ | ✘ | ✘ | ✘ | ✘ | ✔ | ☐ |
| D5 | ✘ | ✘ | ✘ | ✘ | ✘ | ✘ | ☐ |

## Resumen por capa

- **L0**: 8/8 tests superados
- **L1**: 3/7 tests superados
- **L2**: 3/6 tests superados
- **L3**: 0/2 tests superados
- **L4**: 3 hallazgos (ruff (reglas S = Bandit, BLE))
- **L5**: 1 de 2 dependencias marcadas
- **L6**: lista de control manual

## Evidencias

- L1 · test_d1_ampliado_entrada_de_humaneval_plus: assert [8, 1, 6] == [1, 6, 8]
- L1 · test_d1_ampliado_identificadores_negativos: assert [3, -2, -1] == [-2, -1, 3]
- L1 · test_d2a_ampliado_nombre_con_apostrofo: assert [] == [4]
- L1 · test_d2a_ampliado_error_de_bd_no_se_oculta: Failed: DID NOT RAISE Error
- L2 · test_d1_propiedad_resultado_ordenado: AssertionError: Contraejemplo mínimo: ([1, 8], [8, 1]) (encontrado en el intento 8; entrada original ([56, 38, 46, 42, 26, 5, 13, 42, 39, 45], [43, 35, 51, -16, 17, 20, 38, -8, 36, 45, 13, 37]))
- L2 · test_d1_propiedad_oraculo_diferencial: AssertionError: Contraejemplo mínimo: ([1, 8], [8, 1]) (encontrado en el intento 8; entrada original ([56, 38, 46, 42, 26, 5, 13, 42, 39, 45], [43, 35, 51, -16, 17, 20, 38, -8, 36, 45, 13, 37]))
- L2 · test_d2a_propiedad_nombres_aleatorios: Failed: Falla con el nombre "'jzPde" (intento 1): devolvió []
- L3 · test_d2b_seguridad_inyeccion_sql: AssertionError: La entrada maliciosa devolvió 5 pedidos de otros clientes
- L3 · test_d3_seguridad_token_no_reproducible_con_semilla: AssertionError: Mismo token con la misma semilla: 7Ba46KPfVobWvMMjlhaE7eHCLfJqINDw
- L4 · ruff S608 línea 24: Possible SQL injection vector through string-based query construction
- L4 · ruff BLE001 línea 27: Do not catch blind exception: `Exception`
- L4 · ruff S311 línea 34: Standard pseudo-random generators are not suitable for cryptographic purposes
- L5 · sqlite-injection-guard: BLOQUEAR (no existe en PyPI: posible alucinación del asistente; no instalar)
