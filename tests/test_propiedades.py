"""Capa L2 · Pruebas basadas en propiedades y prueba diferencial contra un oráculo.

En lugar de fijar a mano la salida esperada de unos pocos casos, se fijan
propiedades que deben cumplirse SIEMPRE y se prueban con cientos de entradas.
"""
import random
import string

import pytest
from conftest import crear_bd
from propiedades_mini import buscar_contraejemplo


def _comprobar(propiedad):
    r = buscar_contraejemplo(propiedad)
    assert r is None, (
        f"Contraejemplo mínimo: {r['minimo']} "
        f"(encontrado en el intento {r['intento']}; entrada original {r['original']})"
    )


def test_d1_propiedad_resultado_ordenado(mod):
    _comprobar(lambda a, b: mod.clientes_comunes(a, b) == sorted(mod.clientes_comunes(a, b)))


def test_d1_propiedad_sin_duplicados(mod):
    _comprobar(lambda a, b: len(mod.clientes_comunes(a, b)) == len(set(mod.clientes_comunes(a, b))))


def test_d1_propiedad_solo_elementos_comunes(mod):
    _comprobar(lambda a, b: all(x in a and x in b for x in mod.clientes_comunes(a, b)))


def test_d1_propiedad_oraculo_diferencial(mod):
    # Oráculo: una implementación de referencia, sencilla y fácil de revisar.
    _comprobar(lambda a, b: mod.clientes_comunes(a, b) == sorted(set(a) & set(b)))


def test_d2a_propiedad_nombres_aleatorios(mod):
    """Para cualquier nombre almacenado, la consulta debe devolver su pedido."""
    rng = random.Random(7)
    alfabeto = string.ascii_letters + " áéíóúñÑ'-"
    for intento in range(1, 201):
        nombre = "".join(rng.choice(alfabeto) for _ in range(rng.randint(1, 12)))
        conn = crear_bd([(1, nombre, "2026-01-01", 1.0)])
        obtenido = [f[0] for f in mod.pedidos_de_cliente(conn, nombre)]
        conn.close()
        if obtenido != [1]:
            pytest.fail(f"Falla con el nombre {nombre!r} (intento {intento}): devolvió {obtenido}")


def test_d3_propiedad_formato_del_token(mod):
    """Propiedad funcional del token: longitud pedida y solo caracteres alfanuméricos."""
    rng = random.Random(11)
    for _ in range(200):
        n = rng.randint(1, 64)
        token = mod.generar_token_restablecimiento(n)
        assert len(token) == n and token.isascii() and token.isalnum()
