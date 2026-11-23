#!/usr/bin/env python3
"""Comprueba las dependencias de un requirements.txt antes de instalarlas.

Detecta paquetes inexistentes (posibles alucinaciones del asistente) y paquetes que
existen pero con señales débiles de legitimidad (una sola versión, sin descripción,
muy recientes). No sustituye a pip-audit, que busca vulnerabilidades conocidas (CVE)
en versiones de paquetes legítimos.

Uso:
    python herramientas/comprobar_dependencias.py caso/requirements_generado.txt
    python herramientas/comprobar_dependencias.py caso/requirements_generado.txt --online
    python herramientas/comprobar_dependencias.py fichero.txt --json salida.json
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

AQUI = pathlib.Path(__file__).resolve().parent
SNAPSHOT = AQUI / "snapshot_pypi_2026-11-22.json"
DIAS_RECIENTE = 90


def normalizar(nombre):
    """Normalización de nombres de PyPI (PEP 503)."""
    return re.sub(r"[-_.]+", "-", nombre).lower()


def leer_requirements(ruta):
    nombres = []
    for linea in pathlib.Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.split("#", 1)[0].strip()
        if not linea or linea.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", linea)
        if m:
            nombres.append(normalizar(m.group(1)))
    return nombres


def consultar_pypi(nombre, timeout=10):
    """Consulta la API JSON de PyPI. Devuelve un dict con los datos relevantes."""
    url = f"https://pypi.org/pypi/{nombre}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            datos = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"existe": False}
        raise
    info = datos.get("info", {})
    fechas = [
        f["upload_time_iso_8601"][:10]
        for ficheros in datos.get("releases", {}).values()
        for f in ficheros
        if f.get("upload_time_iso_8601")
    ]
    descripcion = (info.get("description") or "").strip()
    return {
        "existe": True,
        "ultima_version": info.get("version"),
        "n_versiones": len(datos.get("releases", {})),
        "primera_publicacion": min(fechas) if fechas else None,
        "descripcion": bool(descripcion) and descripcion.upper() != "UNKNOWN",
        "resumen": info.get("summary"),
        "repositorio": bool(info.get("project_urls") or info.get("home_page")),
    }


def evaluar(nombre, datos, hoy=None):
    """Asigna un veredicto a partir de los datos del paquete."""
    hoy = hoy or dt.datetime.now(dt.timezone.utc).date()
    if not datos.get("existe"):
        return "BLOQUEAR", ["no existe en PyPI: posible alucinación del asistente; no instalar"]
    senales = []
    if datos.get("n_versiones") == 1:
        senales.append("una sola versión publicada")
    if datos.get("descripcion") is False:
        senales.append("sin descripción del proyecto")
    if datos.get("repositorio") is False:
        senales.append("sin enlace a repositorio ni web")
    primera = datos.get("primera_publicacion")
    if primera:
        edad = (hoy - dt.date.fromisoformat(primera)).days
        if edad < DIAS_RECIENTE:
            senales.append(f"publicado hace solo {edad} días")
    if datos.get("nota"):
        senales.append(datos["nota"])
    if senales:
        return "REVISAR", senales
    return "OK", ["existe; comprobar además vulnerabilidades conocidas (pip-audit)"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("requirements")
    ap.add_argument("--online", action="store_true", help="consultar PyPI en vez del snapshot")
    ap.add_argument("--json", help="guardar el resultado en este fichero JSON")
    args = ap.parse_args(argv)

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    resultados = []
    for nombre in leer_requirements(args.requirements):
        if args.online:
            datos, fuente = consultar_pypi(nombre), "PyPI (en línea)"
        elif nombre in snapshot:
            datos, fuente = snapshot[nombre], f"snapshot {snapshot['_meta']['fecha_consulta']}"
        else:
            datos, fuente = None, "sin datos (usa --online)"
        if datos is None:
            veredicto, motivos = "SIN DATOS", ["no está en el snapshot; ejecuta con --online"]
        else:
            veredicto, motivos = evaluar(nombre, datos)
        resultados.append({"paquete": nombre, "veredicto": veredicto, "motivos": motivos, "fuente": fuente})
        print(f"[{veredicto:^9}] {nombre:<26} {'; '.join(motivos)}  ({fuente})")

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if any(r["veredicto"] in ("BLOQUEAR", "REVISAR", "SIN DATOS") for r in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
