"""Mini motor de pruebas basadas en propiedades (solo biblioteca estándar).

Hace, en pequeño, lo que hacen Hypothesis (Python) o QuickCheck (Haskell):
1. genera muchas entradas aleatorias, reproducibles gracias a una semilla fija;
2. comprueba una propiedad que debe cumplirse para CUALQUIER entrada válida;
3. si encuentra un contraejemplo, lo reduce («shrinking») hasta uno mínimo.

En un proyecto real se usaría Hypothesis:  pip install hypothesis
"""
import random


def generar_lista(rng, n_max=12, minimo=-20, maximo=60):
    return [rng.randint(minimo, maximo) for _ in range(rng.randint(0, n_max))]


def _variantes(args):
    """Candidatos más simples: quitar un elemento o acercar un valor a 0
    (el valor se sustituye en todas las listas a la vez para no romper lo que comparten)."""
    for k, lista in enumerate(args):
        for i in range(len(lista)):
            quitar = [list(a) for a in args]
            del quitar[k][i]
            yield quitar
    valores = sorted({v for lista in args for v in lista}, key=abs, reverse=True)
    for v in valores:
        for nuevo in (0, v // 2, v - 1 if v > 0 else v + 1):
            if nuevo != v and abs(nuevo) < abs(v):
                yield [[nuevo if x == v else x for x in lista] for lista in args]


def reducir(propiedad, args):
    """Reduce un contraejemplo mientras la propiedad siga fallando."""
    actual = [list(a) for a in args]
    mejorado = True
    while mejorado:
        mejorado = False
        for candidato in _variantes(actual):
            if not propiedad(*candidato):
                actual = candidato
                mejorado = True
                break
    return tuple(actual)


def buscar_contraejemplo(propiedad, n_casos=300, semilla=2026, n_args=2):
    """Devuelve None si la propiedad se cumple en todos los casos generados."""
    rng = random.Random(semilla)
    for intento in range(1, n_casos + 1):
        args = tuple(generar_lista(rng) for _ in range(n_args))
        if not propiedad(*args):
            return {"intento": intento, "original": args, "minimo": reducir(propiedad, args)}
    return None
