"""Módulo de pedidos después de pasar por las capas de verificación (versión corregida)."""
import secrets
import sqlite3
import string

_ALFABETO = string.ascii_letters + string.digits


def clientes_comunes(campana_a: list, campana_b: list) -> list:
    """Devuelve los identificadores comunes a ambas campañas, ordenados y sin repetir."""
    return sorted(set(campana_a) & set(campana_b))


def pedidos_de_cliente(conn: sqlite3.Connection, cliente: str) -> list:
    """Devuelve los pedidos (id, fecha, importe) de un cliente, ordenados por fecha.

    - Consulta parametrizada: el valor de ``cliente`` nunca se interpreta como SQL.
    - Los errores de la base de datos se propagan; no se disfrazan de «sin pedidos».
    - Pendiente de diseño (D5): quién puede consultar a qué cliente se decide en la
      capa que llama a esta función, con la identidad del usuario autenticado.
    """
    consulta = "SELECT id, fecha, importe FROM pedidos WHERE cliente = ? ORDER BY fecha, id"
    return conn.execute(consulta, (cliente,)).fetchall()


def generar_token_restablecimiento(longitud: int = 32) -> str:
    """Genera el token con un generador criptográficamente seguro (módulo secrets)."""
    return "".join(secrets.choice(_ALFABETO) for _ in range(longitud))
