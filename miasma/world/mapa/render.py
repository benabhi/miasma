# -*- coding: utf-8 -*-
"""
Dibuja el mapa a partir de las salas que existen en la base, no de los datos.

La diferencia importa: el mapa se arma recorriendo las salidas reales de cada
sala, así que si abrís un pasaje nuevo in-game el mapa lo refleja sin tocar
`ubicaciones.py`. Los datos solo dicen dónde cae cada sala; qué se puede
caminar lo dicen las salidas.

Entre dos celdas contiguas va un espacio si hay paso y un muro si no. Una fila
separadora solo se dibuja si tiene al menos un muro: si dos filas están
completamente abiertas, quedan pegadas y el mapa se lee como una calle.
"""

from evennia.utils import ansi

from world.mapa import iconos

# Desplazamiento en la grilla de cada dirección cardinal.
DESPLAZAMIENTOS = {
    "norte": (0, 1),
    "sur": (0, -1),
    "este": (1, 0),
    "oeste": (-1, 0),
}


# --------------------------------------------------------------------------
# Lectura de las salas
# --------------------------------------------------------------------------


def posicion(sala):
    """
    Coordenada de una sala en su plano, o None si es un interior anclado.

    Returns:
        tuple or None: `(plano, x, y, z)`.

    """
    if not sala:
        return None
    plano = sala.db.plano
    pos = sala.db.pos
    if not plano or not pos:
        return None
    return (plano, pos[0], pos[1], pos[2])


def ancla_de(sala):
    """
    Sala desde la que se dibuja el mapa cuando el jugador está en un interior.

    Los interiores de una sola sala no tienen celda propia: se dibuja la calle
    de la que se entra. Si el ancla tampoco tiene celda —un interior dentro de
    otro, como la habitación del motel— se sigue la cadena.

    """
    visitadas = set()
    actual = sala
    while actual and actual.id not in visitadas:
        if posicion(actual):
            return actual
        visitadas.add(actual.id)
        actual = actual.db.ancla
    return None


def _salas_del_plano(plano, z):
    """Todas las salas de un plano en un nivel dado, indexadas por (x, y)."""
    from evennia.utils import search

    grilla = {}
    for sala in search.search_tag("silent_hill", category="mapa"):
        if sala.destination is not None:
            continue
        datos = posicion(sala)
        if not datos:
            continue
        s_plano, x, y, s_z = datos
        if s_plano == plano and s_z == z:
            grilla[(x, y)] = sala
    return grilla


def _hay_paso(desde, hasta):
    """True si se puede ir de una sala a la otra, en cualquiera de los dos sentidos."""
    if not desde or not hasta:
        return False
    if any(salida.destination == hasta for salida in desde.exits):
        return True
    return any(salida.destination == desde for salida in hasta.exits)


def _separacion(a, b):
    """
    True si entre dos celdas hay que dibujar un muro.

    Solo se dibuja entre dos salas que existen y no se comunican. Si de un lado
    no hay nada, el mapa simplemente termina ahí: el vacío ya dice que no se
    puede seguir, y llenarlo de muros deja el mapa ilegible.

    """
    if a is None or b is None:
        return False
    return not _hay_paso(a, b)


# --------------------------------------------------------------------------
# Dibujo
# --------------------------------------------------------------------------


def _esquina(muro_h_izq, muro_h_der, muro_v_arr, muro_v_aba):
    """Carácter donde se cruzan las separaciones de cuatro celdas."""
    horizontal = muro_h_izq or muro_h_der
    vertical = muro_v_arr or muro_v_aba
    if horizontal and vertical:
        return iconos.MURO_ESQUINA
    if horizontal:
        return iconos.MURO_HORIZONTAL
    if vertical:
        return iconos.MURO_VERTICAL
    return iconos.PASO


def dibujar(sala_actual, radio=3, enmarcar=True, recortar=True):
    """
    Arma el mapa centrado en la sala del jugador.

    Args:
        sala_actual (Room): dónde está parado el jugador.
        radio (int): cuántas celdas mostrar a cada lado del centro.
        enmarcar (bool): rodear el mapa con un recuadro.
        recortar (bool): achicar la ventana hasta lo que realmente existe. Para
            el mapa grande conviene; para el minimapa de `mirar` no, porque el
            ancho cambiaría de sala en sala y la columna de texto bailaría a
            cada paso.

    Returns:
        tuple: `(lineas, tipos)`. `lineas` es una lista de strings ya listos
        para imprimir; `tipos` es el conjunto de tipos de sala que aparecen,
        para poder armar la leyenda.

    """
    centro = sala_actual if posicion(sala_actual) else ancla_de(sala_actual)
    if not centro:
        return ([], set())

    plano, cx, cy, cz = posicion(centro)
    grilla = _salas_del_plano(plano, cz)
    if not grilla:
        return ([], set())

    x_desde, x_hasta = cx - radio, cx + radio
    y_desde, y_hasta = cy - radio, cy + radio

    ocupadas = [
        (x, y)
        for (x, y) in grilla
        if x_desde <= x <= x_hasta and y_desde <= y <= y_hasta
    ]
    if not ocupadas:
        return ([], set())
    if recortar:
        x_desde = min(x for x, _ in ocupadas)
        x_hasta = max(x for x, _ in ocupadas)
        y_desde = min(y for _, y in ocupadas)
        y_hasta = max(y for _, y in ocupadas)

    tipos = set()

    def muro_horizontal(x, y):
        """True si hay muro entre (x, y) y la celda de abajo."""
        return _separacion(grilla.get((x, y)), grilla.get((x, y - 1)))

    def muro_vertical(x, y):
        """True si hay muro entre (x, y) y la celda de la derecha."""
        return _separacion(grilla.get((x, y)), grilla.get((x + 1, y)))

    lineas = []
    for y in range(y_hasta, y_desde - 1, -1):
        # --- fila de celdas ---
        fila = []
        for x in range(x_desde, x_hasta + 1):
            sala = grilla.get((x, y))
            if not sala:
                fila.append(iconos.ICONO_VACIO)
            elif sala == centro:
                # El jugador va encima de su celda. Si está en un interior
                # anclado, el marcador cae igual sobre la calle de entrada.
                fila.append(f"|y{iconos.ICONO_JUGADOR}|n")
                tipos.add(sala.db.tipo_mapa)
            else:
                tipo = sala.db.tipo_mapa
                tipos.add(tipo)
                fila.append(iconos.icono_de(tipo))
            if x < x_hasta:
                fila.append(
                    iconos.MURO_VERTICAL if muro_vertical(x, y) else iconos.PASO
                )
        lineas.append("".join(fila))

        # --- fila separadora, solo si hay algún muro ---
        if y == y_desde:
            continue
        separadores = [muro_horizontal(x, y) for x in range(x_desde, x_hasta + 1)]
        if not any(separadores) and recortar:
            # Con la ventana recortada se saltean las filas totalmente
            # abiertas, y el mapa queda compacto. Con ventana fija no: la
            # altura tiene que ser siempre la misma.
            continue
        sep = []
        for i, x in enumerate(range(x_desde, x_hasta + 1)):
            sep.append(iconos.MURO_HORIZONTAL if separadores[i] else iconos.PASO)
            if x < x_hasta:
                sep.append(
                    _esquina(
                        separadores[i],
                        separadores[i + 1],
                        muro_vertical(x, y),
                        muro_vertical(x, y - 1),
                    )
                )
        lineas.append("".join(sep))

    if enmarcar:
        ancho = max(len(ansi.strip_ansi(l)) for l in lineas)
        lineas = [f"|x│|n{l}{' ' * (ancho - len(ansi.strip_ansi(l)))}|x│|n" for l in lineas]
        tapa = "|x" + "─" * ancho + "|n"
        lineas = [f"|x┌|n{tapa}|x┐|n"] + lineas + [f"|x└|n{tapa}|x┘|n"]

    return (lineas, tipos)


def niveles_del_plano(plano):
    """Lista ordenada de los niveles (z) que tiene un plano."""
    from evennia.utils import search

    niveles = set()
    for sala in search.search_tag("silent_hill", category="mapa"):
        if sala.destination is not None:
            continue
        datos = posicion(sala)
        if datos and datos[0] == plano:
            niveles.add(datos[3])
    return sorted(niveles)
