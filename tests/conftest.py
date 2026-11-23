"""Configuración común: elige la versión del módulo a verificar y crea una BD de prueba.

La versión se selecciona con la variable de entorno MODULO, por ejemplo:
    MODULO=generado  pytest tests/          (por defecto)
    MODULO=corregido pytest tests/
    MODULO=chatgpt_1 pytest tests/          (busca caso/pedidos_chatgpt_1.py)
"""
import importlib
import os
import pathlib
import sqlite3
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "caso"))

# Datos sintéticos: no corresponden a personas reales.
PEDIDOS = [
    (1, "Ana", "2026-03-02", 120.0),
    (2, "Luis", "2026-01-15", 75.5),
    (3, "Ana", "2026-01-20", 40.0),
    (4, "O'Brien", "2026-02-10", 310.0),
    (5, "Marta", "2026-02-28", 15.0),
]


def crear_bd(filas=PEDIDOS):
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE pedidos (id INTEGER PRIMARY KEY, cliente TEXT, fecha TEXT, importe REAL)"
    )
    conn.executemany("INSERT INTO pedidos VALUES (?, ?, ?, ?)", filas)
    return conn


@pytest.fixture(scope="session")
def mod():
    nombre = os.environ.get("MODULO", "generado")
    if not nombre.startswith("pedidos_"):
        nombre = f"pedidos_{nombre}"
    return importlib.import_module(nombre)


@pytest.fixture
def conn():
    c = crear_bd()
    yield c
    c.close()
