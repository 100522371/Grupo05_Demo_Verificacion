#!/usr/bin/env python3
"""Ejecuta todas las capas de verificación sobre una versión del módulo y genera la matriz
«qué detecta cada capa».

Uso (desde la carpeta raíz de la demo):
    python herramientas/ejecutar_demo.py --version generado
    python herramientas/ejecutar_demo.py --version corregido
    python herramientas/ejecutar_demo.py --version chatgpt_1 --online

--version X verifica caso/pedidos_X.py y, si existe, caso/requirements_X.txt.
Requisitos: Python 3.10+, pytest y ruff (opcional: bandit para comparar con ruff).
"""
import argparse
import csv
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))
import comprobar_dependencias as dep

DEFECTOS = {
    "D1": "clientes_comunes(): salida desordenada (fallo real documentado por EvalPlus)",
    "D2a": "pedidos_de_cliente(): oculta errores y falla con apóstrofos (CWE-390)",
    "D2b": "pedidos_de_cliente(): inyección SQL (CWE-89)",
    "D3": "generar_token_restablecimiento(): aleatoriedad predecible (CWE-330)",
    "D4": "requirements: paquete inexistente sugerido por el asistente",
    "D5": "Diseño: nadie comprueba quién puede consultar los pedidos (CWE-862)",
}

CAPAS = [
    ("L0", "Tests base", "tests/test_base.py"),
    ("L1", "Tests ampliados", "tests/test_ampliados.py"),
    ("L2", "Propiedades", "tests/test_propiedades.py"),
    ("L3", "Tests seguridad", "tests/test_seguridad.py"),
    ("L4", "Análisis estático", None),
    ("L5", "Dependencias", None),
    ("L6", "Revisión humana", None),
]

# Reglas de análisis estático -> defecto (ruff implementa las reglas de Bandit como "S...")
REGLAS = {"S608": "D2b", "B608": "D2b", "S311": "D3", "B311": "D3",
          "BLE001": "D2a", "S110": "D2a", "B110": "D2a"}

LISTA_REVISION = [
    ("D1", "¿La salida cumple TODO el contrato (orden, duplicados), no solo los ejemplos?"),
    ("D2a", "¿Hay except genéricos que convierten un error en un resultado «normal»?"),
    ("D2b", "¿Se construye SQL concatenando datos que vienen del usuario?"),
    ("D3", "¿Los secretos (tokens, claves) usan un generador criptográfico (secrets)?"),
    ("D4", "¿Cada dependencia es necesaria, existe y procede de un proyecto conocido?"),
    ("D5", "¿Quién puede llamar a esta función y sobre qué datos? (autorización)"),
]


def ejecutar_pytest(capa, fichero, version, carpeta):
    xml = carpeta / f"{capa}_{version}.xml"
    env = dict(os.environ, MODULO=version, PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-m", "pytest", fichero, "-q", "-p", "no:cacheprovider",
           f"--junitxml={xml}"]
    proc = subprocess.run(cmd, cwd=RAIZ, env=env, capture_output=True, text=True, check=False)
    (carpeta / f"{capa}_{version}.log").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    resultados = []
    for caso in ET.parse(xml).getroot().iter("testcase"):
        fallo = caso.find("failure")
        if fallo is None:
            fallo = caso.find("error")
        mensaje = ""
        if fallo is not None:
            mensaje = (fallo.get("message") or "").splitlines()[0][:220]
        m = re.match(r"test_(d1|d2a|d2b|d3)_", caso.get("name", ""))
        resultados.append({
            "test": caso.get("name"),
            "defecto": m.group(1).upper().replace("D2A", "D2a").replace("D2B", "D2b") if m else None,
            "ok": fallo is None,
            "mensaje": mensaje,
        })
    return resultados


def ejecutar_sast(modulo, carpeta, version):
    hallazgos, herramientas = [], []
    if shutil.which("ruff"):
        herramientas.append("ruff (reglas S = Bandit, BLE)")
        proc = subprocess.run(
            ["ruff", "check", "--no-cache", "--select", "S,BLE", "--output-format", "json", str(modulo)],
            cwd=RAIZ, capture_output=True, text=True, check=False)
        for h in json.loads(proc.stdout or "[]"):
            hallazgos.append({"herramienta": "ruff", "regla": h["code"],
                              "linea": h["location"]["row"], "mensaje": h["message"]})
    if shutil.which("bandit"):
        herramientas.append("bandit")
        proc = subprocess.run(["bandit", "-q", "-f", "json", str(modulo)],
                              cwd=RAIZ, capture_output=True, text=True, check=False)
        for h in json.loads(proc.stdout or "{}").get("results", []):
            hallazgos.append({"herramienta": "bandit", "regla": h["test_id"],
                              "linea": h["line_number"], "mensaje": h["issue_text"]})
    (carpeta / f"L4_{version}.json").write_text(
        json.dumps({"herramientas": herramientas, "hallazgos": hallazgos}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    return herramientas, hallazgos


def comprobar_requirements(ruta, online, carpeta, version):
    if not ruta.exists():
        return []
    salida = carpeta / f"L5_{version}.json"
    argumentos = [str(ruta), "--json", str(salida)] + (["--online"] if online else [])
    dep.main(argumentos)
    return json.loads(salida.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="generado")
    ap.add_argument("--online", action="store_true", help="consultar PyPI en lugar del snapshot")
    args = ap.parse_args()

    version = args.version
    modulo = RAIZ / "caso" / f"pedidos_{version}.py"
    requirements = RAIZ / "caso" / f"requirements_{version}.txt"
    if not modulo.exists():
        sys.exit(f"No existe {modulo}")
    carpeta = RAIZ / "resultados"
    carpeta.mkdir(exist_ok=True)

    print(f"\n=== Verificando caso/pedidos_{version}.py ===\n")
    detectado = {d: {c[0]: False for c in CAPAS} for d in DEFECTOS}
    evidencias = {c[0]: [] for c in CAPAS}
    resumen = {}

    for capa, nombre, fichero in CAPAS[:4]:
        res = ejecutar_pytest(capa, fichero, version, carpeta)
        fallidos = [r for r in res if not r["ok"]]
        resumen[capa] = f"{len(res) - len(fallidos)}/{len(res)} tests superados"
        print(f"{capa} {nombre:<18} {resumen[capa]}")
        for r in fallidos:
            print(f"    ✘ {r['test']}: {r['mensaje']}")
            if r["defecto"]:
                detectado[r["defecto"]][capa] = True
            evidencias[capa].append(f"{r['test']}: {r['mensaje']}")

    herramientas, hallazgos = ejecutar_sast(modulo, carpeta, version)
    resumen["L4"] = (f"{len(hallazgos)} hallazgos ({', '.join(herramientas)})"
                     if herramientas else "no ejecutado: instala ruff o bandit")
    print(f"L4 Análisis estático  {resumen['L4']}")
    for h in hallazgos:
        print(f"    ⚠ {h['herramienta']} {h['regla']} (línea {h['linea']}): {h['mensaje']}")
        if h["regla"] in REGLAS:
            detectado[REGLAS[h["regla"]]]["L4"] = True
        evidencias["L4"].append(f"{h['herramienta']} {h['regla']} línea {h['linea']}: {h['mensaje']}")

    print("L5 Dependencias")
    deps = comprobar_requirements(requirements, args.online, carpeta, version)
    marcadas = [d for d in deps if d["veredicto"] in ("BLOQUEAR", "REVISAR")]
    resumen["L5"] = (f"{len(marcadas)} de {len(deps)} dependencias marcadas" if deps
                     else "sin requirements para esta versión")
    if marcadas:
        detectado["D4"]["L5"] = True
    for d in marcadas:
        evidencias["L5"].append(f"{d['paquete']}: {d['veredicto']} ({'; '.join(d['motivos'])})")

    print("L6 Revisión humana    lista de control (manual, no automatizable):")
    for d, pregunta in LISTA_REVISION:
        print(f"    ☐ [{d}] {pregunta}")
    resumen["L6"] = "lista de control manual"

    # ---- Matriz ----
    automaticas = [c for c in CAPAS if c[0] != "L6"]
    cabecera = ["Defecto"] + [f"{c[0]} {c[1]}" for c in CAPAS]
    filas = []
    for d in DEFECTOS:
        fila = [d] + ["✔" if detectado[d][c[0]] else "✘" for c in automaticas] + ["☐"]
        filas.append(fila)

    print("\nMatriz: ¿qué capa detecta cada defecto?  (✔ detectado · ✘ no detectado · ☐ depende del revisor)\n")
    anchos = [7] + [max(4, len(c[0])) for c in CAPAS]
    print("  ".join(h[:2].ljust(a) if i else h.ljust(a) for i, (h, a) in enumerate(zip(cabecera, anchos))))
    for fila in filas:
        print("  ".join(v.ljust(a) for v, a in zip(fila, anchos)))
    print()
    for d, texto in DEFECTOS.items():
        print(f"  {d:<4} {texto}")
    sin_auto = [d for d in DEFECTOS if not any(detectado[d][c[0]] for c in automaticas)]
    if len(sin_auto) == len(DEFECTOS):
        print("\n  Ninguna capa automática encuentra defectos en esta versión. Eso no prueba que no los"
              "\n  haya: D5 (autorización) solo se puede comprobar en el diseño y la revisión humana (L6).")
    elif sin_auto:
        print(f"\n  Ninguna capa automática detecta: {', '.join(sin_auto)}")

    # ---- Guardar resultados ----
    datos = {"version": version, "resumen": resumen, "detectado": detectado,
             "evidencias": evidencias, "defectos": DEFECTOS,
             "capas": {c[0]: c[1] for c in CAPAS}}
    (carpeta / f"matriz_{version}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                                                    encoding="utf-8")
    with open(carpeta / f"matriz_{version}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cabecera)
        w.writerows(filas)
    lineas = [f"# Matriz de detección · versión `{version}`", "",
              "| " + " | ".join(cabecera) + " |", "|" + "---|" * len(cabecera)]
    lineas += ["| " + " | ".join(f) + " |" for f in filas]
    lineas += ["", "## Resumen por capa", ""] + [f"- **{k}**: {v}" for k, v in resumen.items()]
    lineas += ["", "## Evidencias", ""]
    for capa, ev in evidencias.items():
        for e in ev:
            lineas.append(f"- {capa} · {e}")
    (carpeta / f"matriz_{version}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nResultados guardados en resultados/matriz_{version}.(md|json|csv)\n")


if __name__ == "__main__":
    main()
