"""Capa L0 · Tests base: los casos típicos que escribiría cualquiera (como en HumanEval).

Los cuatro tests de clientes_comunes son los de la tarea HumanEval/58.
"""


def test_d1_base_ejemplo_docstring_1(mod):
    assert mod.clientes_comunes([1, 4, 3, 34, 653, 2, 5], [5, 7, 1, 5, 9, 653, 121]) == [1, 5, 653]


def test_d1_base_ejemplo_docstring_2(mod):
    assert mod.clientes_comunes([5, 3, 2, 8], [3, 2]) == [2, 3]


def test_d1_base_tres_comunes(mod):
    assert mod.clientes_comunes([4, 3, 2, 8], [3, 2, 4]) == [2, 3, 4]


def test_d1_base_segunda_lista_vacia(mod):
    assert mod.clientes_comunes([4, 3, 2, 8], []) == []


def test_d2a_base_pedidos_ordenados_por_fecha(conn, mod):
    filas = mod.pedidos_de_cliente(conn, "Ana")
    assert [f[0] for f in filas] == [3, 1]


def test_d2a_base_cliente_sin_pedidos(conn, mod):
    assert mod.pedidos_de_cliente(conn, "Pedro") == []


def test_d3_base_longitud_y_alfabeto(mod):
    token = mod.generar_token_restablecimiento()
    assert len(token) == 32 and token.isascii() and token.isalnum()


def test_d3_base_dos_tokens_distintos(mod):
    assert mod.generar_token_restablecimiento() != mod.generar_token_restablecimiento()
