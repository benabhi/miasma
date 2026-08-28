# -*- coding: utf-8 -*-
"""
Exporta Nébrida al formato de mapa de TinTin++.

    docker compose exec game evennia shell -c "from world.mapa.exportar_tintin import exportar; exportar()"

El archivo que sale (`nebrida.map`) se carga desde `miasma.tin` con
`#map read`, así que el jugador arranca con la ciudad entera dibujada en vez de
tener que caminarla para descubrirla.

|ySobre el formato.|n No está documentado: se sacó leyendo `map_read` y la
escritura del archivo en `src/mapper.c` de TinTin++ 2.02.20. Lo que espera:

- La primera línea tiene que ser `C <tamaño>` o aborta la lectura.
- Después, una línea por registro, identificada por su primera letra:
  `V` versión, `F` banderas, `G` vnum global, `I` sala inicial,
  `R` una sala, `E` una salida de la última sala declarada.
- Los campos van entre llaves, en orden fijo.
- Las líneas en blanco se ignoran; cualquier otra primera letra es un error.

Se exporta solo el plano de la ciudad. Los interiores con plano propio -el
hospital, las alcantarillas- se entran por salidas que no son puntos cardinales
(`dentro`, `escalera`), y TinTin++ arma la posición de cada sala siguiendo las
direcciones: sin un cardinal que las ate, quedarían flotando.
"""

import os

from django.conf import settings
from evennia.utils import search

from world.mapa import iconos

# El plano que se exporta y el archivo que se escribe.
PLANO = "nebrida"
# Va dentro del gamedir porque es lo único que el contenedor tiene montado
# desde el host. Desde la raíz del repo, el archivo queda en miasma/nebrida.map,
# que es la ruta que usa miasma.tin.
ARCHIVO = os.path.join(settings.GAME_DIR, "nebrida.map")

# Cómo se llama cada dirección en TinTin++ y qué bit le corresponde.
# Los valores salen de `MAP_EXIT_*` en src/tintin.h: N=1, E=2, S=4, W=8,
# U=16, D=32, y las diagonales son la suma de sus dos componentes.
DIRECCIONES = {
    "norte": ("n", 1),
    "este": ("e", 2),
    "sur": ("s", 4),
    "oeste": ("w", 8),
    "arriba": ("u", 16),
    "abajo": ("d", 32),
    "noreste": ("ne", 3),
    "sureste": ("se", 6),
    "noroeste": ("nw", 9),
    "suroeste": ("sw", 12),
}

# Banderas del mapa (MAP_FLAG_* en src/tintin.h):
#   STATIC 1   el mapa no crea salas al caminar
#   VTMAP  2   se dibuja en la franja de arriba de la pantalla
BANDERAS = 1 | 2


# Evennia escribe el color como |rgb con cada canal de 0 a 5 -el cubo de 216
# colores de xterm256-. TinTin++ lo escribe como <Frgb> con cada canal en un
# dígito hexadecimal, de 0 a F, y lo emite como color verdadero.
#
# La tabla lleva cada nivel de Evennia al dígito que más se le parece. Los
# niveles del cubo no están repartidos parejo -son 0, 95, 135, 175, 215 y 255-,
# así que dividir por 17 y redondear da 0, 6, 8, A, D, F y no una escala lineal.
NIVELES = "068ADF"


def _color_tintin(tipo):
    """Traduce el color de un tipo de celda al formato de TinTin++.

    |yOjo con la forma de tres dígitos.|n `<025>` existe en TinTin++ pero
    significa otra cosa: estilo 0, frente 2, fondo 5. Escribir ahí los dígitos
    de Evennia tal cual pinta fondos macizos y el mapa se vuelve ilegible.

    """
    color = iconos.COLORES.get(tipo, "")
    if len(color) != 4 or not color.startswith("|") or not color[1:].isdigit():
        return ""
    canales = [int(c) for c in color[1:]]
    if max(canales) > 5:
        return ""
    return "<F%s>" % "".join(NIVELES[c] for c in canales)


def _simbolo(sala):
    """El carácter con el que se dibuja la sala, el mismo que usa el juego."""
    tipo = sala.db.tipo_mapa or "interior"
    if sala.db.puerta_visible:
        return iconos.ICONO_PUERTA
    return iconos.icono_de(tipo, sala.db.vecinos_trama)


def _llaves(texto):
    """Las llaves delimitan los campos, así que adentro no pueden aparecer."""
    return str(texto).replace("{", "(").replace("}", ")")


def exportar(ruta=None, informar=print):
    """
    Escribe el mapa de la ciudad en formato TinTin++.

    Args:
        ruta (str, optional): dónde escribirlo. Por defecto,
            `miasma/nebrida.map`.
        informar (callable): por dónde contar lo que va pasando.

    Returns:
        dict: resumen de lo exportado.

    """
    ruta = ruta or ARCHIVO

    salas = [
        obj
        for obj in search.search_tag("nebrida", category="mapa")
        if obj.destination is None and obj.db.plano == PLANO
    ]
    salas.sort(key=lambda o: o.db.pos)

    # La sala de inicio se numera 1: TinTin++ empieza a dibujar desde ahí.
    inicio = int(settings.START_LOCATION.lstrip("#"))
    salas.sort(key=lambda o: (o.id != inicio, o.db.pos))
    vnum = {sala.id: numero for numero, sala in enumerate(salas, start=1)}

    lineas = [
        f"C {len(salas) + 2}",
        "",
        "V 2020",
        "",
        f"F {BANDERAS}",
        "",
        "G 0",
        "",
        f"I {vnum.get(inicio, 1)}",
        "",
    ]

    salidas_escritas = salidas_omitidas = 0
    for sala in salas:
        tipo = sala.db.tipo_mapa or "interior"
        lineas.append(
            "R {%d} {0} {%s} {%s} {%s} {} {%s} {} {} {} {1.000} {}"
            % (
                vnum[sala.id],
                _color_tintin(tipo),
                _llaves(sala.key),
                _llaves(_simbolo(sala)),
                _llaves(tipo),
            )
        )
        for salida in sala.exits:
            destino = salida.destination
            if destino is None or destino.id not in vnum:
                salidas_omitidas += 1
                continue
            if salida.key not in DIRECCIONES:
                salidas_omitidas += 1
                continue
            nombre, bit = DIRECCIONES[salida.key]
            lineas.append(
                "E {%d} {%s} {%s} {%d} {0} {} {1.000} {} {0.00}"
                % (vnum[destino.id], nombre, salida.key, bit)
            )
            salidas_escritas += 1
        lineas.append("")

    with open(ruta, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lineas) + "\n")

    informar(
        f"Mapa exportado a {os.path.abspath(ruta)}: "
        f"{len(salas)} salas, {salidas_escritas} salidas "
        f"({salidas_omitidas} omitidas por no ser puntos cardinales)."
    )
    return {
        "archivo": os.path.abspath(ruta),
        "salas": len(salas),
        "salidas": salidas_escritas,
        "omitidas": salidas_omitidas,
    }
