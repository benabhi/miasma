# -*- coding: utf-8 -*-
"""
Iconos del minimapa.

Cada celda del mapa declara un *tipo* (calle, comercio, iglesia…) y de acá sale
el carácter con el que se dibuja. Se trabaja con tipos y no con caracteres
sueltos para poder cambiar toda la estética del mapa desde un solo lugar.

|ySobre la elección de caracteres.|n La primera versión usaba formas geométricas
y símbolos lindos (▤ ▣ ✚ ⦿ † ◊) y en la práctica salían cuadraditos vacíos: las
fuentes monoespaciadas que usan los clientes MUD no cubren esos bloques
Unicode. Un mapa ilegible no sirve por más elegante que sea el carácter, así
que este set se limita a:

- **Bloques de sombreado** (`░ ▒ ▓ █`) y **dibujo de cajas** (`─ │ ═ ║ ╬`), que
  vienen de CP437 y están en cualquier fuente monoespaciada.
- **ASCII puro** para todo lo demás, al estilo de los roguelikes: `#` edificio,
  `$` comercio, `+` iglesia, `@` el jugador.

Si algún día usás una fuente con buena cobertura Unicode (Fira Code, Cascadia,
DejaVu Sans Mono), cambiar este archivo alcanza para volver a los símbolos
bonitos. Nada más lee estos caracteres.

Los emoji quedan descartados siempre: ocupan dos columnas y descuadran la
grilla entera.
"""

# --------------------------------------------------------------------------
# Tipos de sala -> carácter
# --------------------------------------------------------------------------

ICONOS = {
    # --- exteriores urbanos ---
    "calle": "░",       # calzada
    "cruce": "▒",       # intersección
    "avenida": "▓",     # vía principal
    "vereda": ",",      # acera, paso peatonal
    "puente": "=",
    "callejon": ":",
    "descampado": ".",  # baldío, terreno vacío
    "estacionamiento": "-",
    # --- edificios ---
    "edificio": "#",
    "casa": "n",
    "comercio": "$",
    "iglesia": "+",
    "escuela": "E",
    "hospital": "H",
    "comisaria": "P",
    "hotel": "M",
    "industria": "%",
    # --- interiores ---
    "interior": "o",
    "pasillo": "-",
    "sala": "o",
    "escalera": "x",
    "sotano": "u",
    "azotea": "^",
    # --- naturaleza y agua ---
    "arbol": "T",
    "agua": "~",
    "muelle": "&",
    "faro": "!",
    # --- subsuelo ---
    "alcantarilla": "v",
    # --- atracciones ---
    "atraccion": "*",
    # --- infranqueable ---
    "muro": "█",
}

# Tipos por los que no se puede caminar: se dibujan, pero no son salas. El
# constructor no crea nada para ellos.
INTRANSITABLES = frozenset(("agua", "arbol", "muro"))

# Con qué se dibuja algo que no declaró tipo. Que se note, para que salte a la
# vista que a esa sala le falta el dato.
ICONO_DESCONOCIDO = "?"

# El jugador, encima del icono de su sala. `@` es el estándar de los
# roguelikes y no falta en ninguna fuente.
ICONO_JUGADOR = "@"

# Relleno donde no hay absolutamente nada, ni sala ni terreno.
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

# Nombre legible de cada tipo, para la referencia del comando `mapa`.
NOMBRES = {
    "calle": "calle",
    "cruce": "cruce",
    "avenida": "avenida",
    "vereda": "vereda",
    "puente": "puente",
    "callejon": "callejón",
    "descampado": "baldío",
    "estacionamiento": "playón",
    "edificio": "edificio",
    "casa": "casa",
    "comercio": "comercio",
    "iglesia": "iglesia",
    "escuela": "escuela",
    "hospital": "hospital",
    "comisaria": "comisaría",
    "hotel": "hotel",
    "industria": "galpón",
    "interior": "interior",
    "pasillo": "pasillo",
    "sala": "sala",
    "escalera": "escalera",
    "sotano": "sótano",
    "azotea": "azotea",
    "arbol": "arboleda",
    "agua": "agua",
    "muelle": "muelle",
    "faro": "faro",
    "alcantarilla": "cloaca",
    "atraccion": "atracción",
    "muro": "muro",
}


def icono_de(tipo):
    """Devuelve el carácter del tipo de sala, o el de desconocido."""
    return ICONOS.get(tipo, ICONO_DESCONOCIDO)


def leyenda(tipos):
    """
    Arma las líneas de referencia para los tipos que aparecen en un mapa.

    Args:
        tipos (iterable): tipos presentes en lo que se está dibujando.

    Returns:
        list: líneas de texto, tres entradas por línea.

    """
    presentes = [t for t in ICONOS if t in set(tipos)]
    lineas = []
    for i in range(0, len(presentes), 4):
        tanda = presentes[i : i + 4]
        lineas.append(
            "  ".join(
                f"|w{ICONOS[t]}|n {NOMBRES.get(t, t):<11}" for t in tanda
            ).rstrip()
        )
    return lineas
