# -*- coding: utf-8 -*-
"""
Iconos del minimapa.

Cada sala declara un *tipo* (calle, comercio, iglesia…) y de acá sale el
carácter con el que se dibuja. Se trabaja con tipos y no con caracteres sueltos
para poder cambiar toda la estética del mapa desde un solo lugar.

|yTodos los caracteres tienen que ser de ancho simple.|n Los emoji (🌲, 🏠) ocupan
dos columnas en la mayoría de las terminales y descuadran la grilla entera, así
que quedan descartados por más lindos que sean. Los símbolos de acá son del
bloque de formas geométricas y de dibujo de cajas, que son de ancho simple en
cualquier cliente MUD razonable.
"""

# --------------------------------------------------------------------------
# Tipos de sala -> carácter
# --------------------------------------------------------------------------

ICONOS = {
    # --- exteriores urbanos ---
    "calle": "░",       # calzada transitable
    "cruce": "▒",       # intersección
    "avenida": "▓",     # vía principal
    "puente": "╫",      # cruce sobre agua
    "callejon": "·",    # pasaje angosto
    "descampado": "˙",  # terreno vacío
    # --- edificios ---
    "edificio": "□",    # edificio genérico
    "casa": "⌂",        # vivienda
    "comercio": "▤",    # negocio, tienda, bar
    "iglesia": "†",
    "escuela": "▣",
    "hospital": "✚",
    "comisaria": "▩",
    "hotel": "▥",
    "industria": "▦",   # galpón, taller, estación de servicio
    # --- interiores ---
    "interior": "▪",    # cualquier sala puertas adentro
    "pasillo": "┼",  # no usar │: se confunde con el marco del mapa
    "sala": "▫",
    "escalera": "≡",
    "sotano": "▼",
    "azotea": "▲",
    # --- naturaleza y agua ---
    "arbol": "♣",
    "agua": "≈",
    "muelle": "╤",
    "faro": "♦",
    # --- subsuelo ---
    "alcantarilla": "◊",
    # --- atracciones ---
    "atraccion": "◉",
}

# Con qué se dibuja algo que no declaró tipo. Que se note, para que salte a la
# vista que a esa sala le falta el dato.
ICONO_DESCONOCIDO = "?"

# El jugador, encima del icono de su sala.
ICONO_JUGADOR = "⦿"

# Relleno de las celdas de la grilla donde no hay ninguna sala.
ICONO_VACIO = " "

# --------------------------------------------------------------------------
# Dibujo de la grilla
#
# Entre dos salas contiguas va un espacio si se puede pasar de una a la otra, y
# un muro si no. Así el mapa no solo dice qué hay: dice por dónde se camina.
# --------------------------------------------------------------------------

MURO_VERTICAL = "║"    # entre dos celdas lado a lado sin paso
MURO_HORIZONTAL = "═"  # entre dos celdas una encima de otra sin paso
MURO_ESQUINA = "╬"     # donde se cruzan dos muros
PASO = " "             # hay conexión

# Marcas de escalera en la propia celda, para que se vea que el mapa sigue
# hacia arriba o hacia abajo.
MARCA_ARRIBA = "▴"
MARCA_ABAJO = "▾"


def icono_de(tipo):
    """Devuelve el carácter del tipo de sala, o el de desconocido."""
    return ICONOS.get(tipo, ICONO_DESCONOCIDO)


def leyenda(tipos):
    """
    Arma las líneas de referencia para los tipos que aparecen en un mapa.

    Args:
        tipos (iterable): tipos de sala presentes en lo que se está dibujando.

    Returns:
        list: líneas de texto, dos columnas por línea.

    """
    presentes = [t for t in ICONOS if t in set(tipos)]
    lineas = []
    for i in range(0, len(presentes), 3):
        tanda = presentes[i : i + 3]
        lineas.append(
            "  ".join(f"|w{ICONOS[t]}|n {t:<12}" for t in tanda).rstrip()
        )
    return lineas
