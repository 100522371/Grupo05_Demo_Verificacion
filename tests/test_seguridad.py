"""Capa L3 · Tests de seguridad: entradas adversarias pensadas por una persona.

Un generador aleatorio casi nunca produce "x' OR '1'='1": para encontrar una
inyección hay que pensar como un atacante (o usar herramientas que lo hagan).
"""
import random


def test_d2b_seguridad_inyeccion_sql(conn, mod):
    filas = mod.pedidos_de_cliente(conn, "x' OR '1'='1")
    assert filas == [], f"La entrada maliciosa devolvió {len(filas)} pedidos de otros clientes"


def test_d3_seguridad_token_no_reproducible_con_semilla(mod):
    # Si fijar la semilla de 'random' reproduce el token, el token depende de un
    # generador pseudoaleatorio no criptográfico: con su estado, se puede predecir.
    random.seed(1234)
    t1 = mod.generar_token_restablecimiento()
    random.seed(1234)
    t2 = mod.generar_token_restablecimiento()
    assert t1 != t2, f"Mismo token con la misma semilla: {t1}"
