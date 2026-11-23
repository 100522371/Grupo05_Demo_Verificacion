"""Capa L1 · Tests ampliados: casos límite y entradas «difíciles» (estilo EvalPlus).

No todos fallan con la versión generada: un caso límite solo descubre un fallo si
toca justo la condición que lo provoca. Por eso se combinan con la capa L2.
"""
import sqlite3

import pytest


def test_d1_ampliado_entrada_de_humaneval_plus(mod):
    # Entrada añadida por HumanEval+ (Liu et al., 2023, fig. 1)
    assert mod.clientes_comunes([6, 8, 1], [6, 8, 1]) == [1, 6, 8]


def test_d1_ampliado_identificadores_negativos(mod):
    assert mod.clientes_comunes([-1, -2, 3], [3, -2, -1]) == [-2, -1, 3]


def test_d1_ampliado_duplicados(mod):
    assert mod.clientes_comunes([7, 7, 2, 2], [2, 7, 7]) == [2, 7]


def test_d2a_ampliado_nombre_con_apostrofo(conn, mod):
    filas = mod.pedidos_de_cliente(conn, "O'Brien")
    assert [f[0] for f in filas] == [4]


def test_d2a_ampliado_nombre_con_tildes_y_espacios(conn, mod):
    conn.execute("INSERT INTO pedidos VALUES (6, 'José Ñúñez', '2026-04-01', 9.99)")
    assert [f[0] for f in mod.pedidos_de_cliente(conn, "José Ñúñez")] == [6]


def test_d2a_ampliado_error_de_bd_no_se_oculta(mod):
    # Una BD sin la tabla "pedidos" es un error, no un cliente sin pedidos.
    vacia = sqlite3.connect(":memory:")
    with pytest.raises(sqlite3.Error):
        mod.pedidos_de_cliente(vacia, "Ana")


def test_d3_ampliado_longitud_personalizada(mod):
    assert len(mod.generar_token_restablecimiento(64)) == 64
