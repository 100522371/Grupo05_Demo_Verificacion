"""Módulo de pedidos tal y como lo devolvió el asistente (versión SIN revisar).

AVISO DOCENTE: este fichero contiene defectos INTENCIONADOS para el seminario.
- clientes_comunes(): mismo cuerpo que el código que ChatGPT generó para
  HumanEval/58 (Liu et al., 2023, fig. 1).
- pedidos_de_cliente() y generar_token_restablecimiento(): reproducen patrones
  de debilidad documentados (CWE-89, CWE-390 y CWE-330).
No usar en producción.
"""
import random
import sqlite3
import string


def clientes_comunes(campana_a: list, campana_b: list) -> list:
    """Devuelve los identificadores comunes a ambas campañas, ordenados y sin repetir."""
    comunes = list(set(campana_a).intersection(set(campana_b)))
    comunes.sort()
    return list(set(comunes))


def pedidos_de_cliente(conn: sqlite3.Connection, cliente: str) -> list:
    """Devuelve los pedidos (id, fecha, importe) de un cliente, ordenados por fecha."""
    consulta = f"SELECT id, fecha, importe FROM pedidos WHERE cliente = '{cliente}' ORDER BY fecha"
    try:
        return conn.execute(consulta).fetchall()
    except Exception:
        return []


def generar_token_restablecimiento(longitud: int = 32) -> str:
    """Genera un token alfanumérico para el enlace de restablecimiento de contraseña."""
    alfabeto = string.ascii_letters + string.digits
    return "".join(random.choices(alfabeto, k=longitud))
