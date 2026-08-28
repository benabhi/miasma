# -*- coding: utf-8 -*-
"""
Iconos del mapa.

Cada celda declara un *tipo* (calle, comercio, iglesia…) y de acá sale el
carácter con el que se dibuja. Se trabaja con tipos y no con caracteres sueltos
para poder cambiar toda la estética del mapa desde un solo lugar.

|ySobre la elección de caracteres.|n Una versión anterior usaba formas
geométricas y símbolos lindos (▤ ▣ ✚ ⦿ † ◊) y en la práctica salían cuadraditos
vacíos: las fuentes monoespaciadas que usan los clientes MUD no cubren esos
bloques Unicode. Un mapa ilegible no sirve por más elegante que sea el
carácter, así que este set se limita a:

- **dibujo de cajas** (`─ │ ┼ ═ ║ ╬` y sus esquinas) y **bloques de sombreado**
  (`░ ▒ ▓ █`), que vienen de CP437 y están en cualquier fuente monoespaciada;
- **ASCII puro** para los edificios, al estilo de los roguelikes: `#` bloque de
  departamentos, `$` comercio, `+` iglesia, `H` hospital, `@` el jugador.

Los emoji quedan descartados siempre: ocupan dos columnas y descuadran la
grilla entera.
"""

# --------------------------------------------------------------------------
# Tipos de celda -> carácter
#
# Las calles no están acá: se dibujan con el juego de esquinas de más abajo,
# porque su carácter depende de hacia dónde sigue la calle.
# --------------------------------------------------------------------------

ICONOS = {
    # --- espacio público ---
    "vereda": "·",
    "plaza": ",",
    "parque": '"',
    "descampado": ".",
    "atraccion": "*",
    "cementerio": "X",
    # --- edificios ---
    "edificio": "#",       # bloque de departamentos
    "casa": "n",
    "comercio": "$",
    "mercado": "&",
    "industria": "%",      # galpón, depósito, taller
    "iglesia": "i",
    "hospital": "H",
    "comisaria": "P",
    "bomberos": "B",
    "escuela": "E",
    "biblioteca": "L",
    "municipalidad": "A",
    "hotel": "U",
    "estacion_tren": "R",
    # --- agua y costa ---
    "agua": "~",
    "muelle": "=",
    "faro": "!",
    # --- subsuelo ---
    "alcantarilla": "v",
    # --- interiores ---
    "interior": "o",
    "sala": "o",
    "pasillo": "-",
    "escalera": "x",
    "sotano": "u",
    "azotea": "^",
    # --- naturaleza e infranqueable ---
    "arbol": "T",
    "muro": "█",
}

# Por acá no se camina nunca: se dibuja, pero no es sala.
INTRANSITABLES = frozenset(("agua", "arbol", "muro"))

# Lo construido que no se atraviesa. De cada grupo de celdas contiguas del mismo
# tipo, el constructor hace sala **solo la celda de la puerta**, marcada con `+`
# en el mapa; el resto se dibuja pero es macizo.
#
# Acá están los edificios singulares: los que son un volumen único con una
# entrada, y en los que pasar de una punta a la otra por adentro tiene que
# significar algo. La trama común de la ciudad —casas, departamentos, locales a
# la calle— queda afuera a propósito: son muchos y chicos, cada celda es una
# vivienda o un negocio distinto, y se entra a cada uno desde la vereda sin
# ceremonia.
CONSTRUCCIONES = frozenset(
    (
        "mercado",
        "industria",
        "iglesia",
        "hospital",
        "comisaria",
        "bomberos",
        "escuela",
        "biblioteca",
        "municipalidad",
        "hotel",
        "estacion_tren",
    )
)

# Lo construido que se camina, pero no de una unidad a la otra. Cada celda que
# da a la vereda es una vivienda o un negocio distinto: se entra desde la calle
# y no desde la casa de al lado. Las celdas que no dan a la calle —el fondo de
# una manzana profunda— se anexan a la unidad frentista más cercana, que es lo
# que son: el fondo de esa casa.
INDEPENDIENTES = frozenset(("casa", "edificio", "comercio"))

ICONO_DESCONOCIDO = "?"
ICONO_JUGADOR = "@"
ICONO_VACIO = " "

# --------------------------------------------------------------------------
# La trama de calles
#
# Una ciudad se reconoce por su trama, y la trama solo se ve si cada tramo se
# dibuja según hacia dónde sigue: la esquina como esquina, el cruce como cruce.
# Con un icono único para toda calle, la retícula se confunde con las manzanas.
#
# Hacia dónde sigue no es un dato que se escriba: lo deduce el constructor
# mirando qué tiene cada celda al lado. Acá solo está el dibujo.
# --------------------------------------------------------------------------

# Clave: (norte, sur, este, oeste) — 1 donde sigue la trama.
ESQUINAS = {
    (1, 1, 1, 1): "┼",
    (1, 1, 1, 0): "├",
    (1, 1, 0, 1): "┤",
    (1, 0, 1, 1): "┴",
    (0, 1, 1, 1): "┬",
    (1, 1, 0, 0): "│",
    (0, 0, 1, 1): "─",
    (1, 0, 1, 0): "└",
    (1, 0, 0, 1): "┘",
    (0, 1, 1, 0): "┌",
    (0, 1, 0, 1): "┐",
    (1, 0, 0, 0): "│",
    (0, 1, 0, 0): "│",
    (0, 0, 1, 0): "─",
    (0, 0, 0, 1): "─",
    (0, 0, 0, 0): "─",
}

# La avenida va en línea doble: es una arteria y se tiene que notar.
A_DOBLE = {
    "┼": "╬", "├": "╠", "┤": "╣", "┴": "╩", "┬": "╦",
    "│": "║", "─": "═", "└": "╚", "┘": "╝", "┌": "╔", "┐": "╗",
}

ESQUINAS_DOBLES = {clave: A_DOBLE[valor] for clave, valor in ESQUINAS.items()}

# El puente cruza el agua: línea gruesa, distinta de la calle que lo alimenta.
ICONO_PUENTE = "≡"

# La diagonal no tiene esquinas: es una sola tirada en oblicuo.
ICONO_DIAGONAL = "/"

# Tipos que forman la trama: se dibujan con esquinas y cuentan como vecinos al
# calcularlas.
TRAMA = frozenset(("calle", "avenida", "diagonal", "puente"))

# Cómo se dibuja cada tipo de la trama que sí tiene esquinas.
DIBUJO_TRAMA = {
    "calle": ESQUINAS,
    "avenida": ESQUINAS_DOBLES,
}

# Entre celda y celda va siempre un espacio. Se probó marcar con un bloque las
# paredes -los pares de salas contiguas sin paso- y el resultado fue un mapa
# sembrado de manchas grises alrededor de cada puerta, que es justo donde nunca
# hay paso lateral. El edificio ya se ve macizo porque se dibuja macizo; no
# hace falta subrayarlo.
PASO = " "
MARCO = "▒"

# La puerta de un edificio. Un carácter propio y no un color más claro: el
# color se pierde en un cliente sin xterm256, y la puerta es lo único del
# edificio con lo que se puede interactuar.
ICONO_PUERTA = "+"

# --------------------------------------------------------------------------
# Nombres legibles, para la referencia del comando `mapa`
# --------------------------------------------------------------------------

NOMBRES = {
    "calle": "calle",
    "avenida": "avenida",
    "diagonal": "diagonal",
    "puente": "puente",
    "vereda": "vereda",
    "plaza": "plaza",
    "parque": "parque",
    "descampado": "baldío",
    "atraccion": "atracción",
    "cementerio": "cementerio",
    "edificio": "departamentos",
    "casa": "casa",
    "comercio": "comercio",
    "mercado": "mercado",
    "industria": "galpón",
    "iglesia": "iglesia",
    "hospital": "hospital",
    "comisaria": "comisaría",
    "bomberos": "bomberos",
    "escuela": "escuela",
    "biblioteca": "biblioteca",
    "municipalidad": "municipalidad",
    "hotel": "hotel",
    "estacion_tren": "estación",
    "agua": "agua",
    "muelle": "muelle",
    "faro": "faro",
    "alcantarilla": "cloaca",
    "interior": "interior",
    "sala": "sala",
    "pasillo": "pasillo",
    "escalera": "escalera",
    "sotano": "sótano",
    "azotea": "azotea",
    "arbol": "arboleda",
    "muro": "muro",
    "puerta": "puerta",
}

# Con qué se muestra cada tipo en la referencia. Las calles se dibujan de once
# formas según la esquina, así que en la referencia van tres representativas:
# si no, el jugador ve un `┘` en el mapa y lo busca en una lista donde solo
# figura `─`.
GLIFOS_REFERENCIA = {
    "calle": "─│┼",
    "avenida": "═║╬",
    "diagonal": "/",
    "puente": "≡",
    "puerta": "+",
}


# --------------------------------------------------------------------------
# Color
#
# El mapa tiene treinta tipos de celda y en blanco y negro se leen todos igual.
# Los colores no son decoración: son la primera lectura. Se agrupan en familias
# para que el ojo entienda de qué se trata antes de identificar el carácter —
# todo lo azul es agua, todo lo rojo es emergencia, todo lo verde es vegetación.
#
# Van en xterm256 (`|rgb`, cada componente de 0 a 5). Evennia los degrada solo
# a los 16 colores ANSI si el cliente no soporta más, así que no hace falta una
# paleta de repuesto.
# --------------------------------------------------------------------------

COLORES = {
    # agua y costa
    "agua": "|025",
    "muelle": "|430",
    "puente": "|430",
    "faro": "|550",
    # vegetación
    "arbol": "|030",
    "parque": "|151",
    "plaza": "|141",
    # la trama
    "calle": "|222",
    "avenida": "|445",
    "diagonal": "|445",
    # vivienda
    "casa": "|321",
    "edificio": "|322",
    "vereda": "|222",
    "descampado": "|211",
    # actividad
    "comercio": "|441",
    "mercado": "|541",
    "hotel": "|431",
    "industria": "|311",
    "estacion_tren": "|411",
    # servicios públicos
    "hospital": "|500",
    "bomberos": "|520",
    "comisaria": "|025",
    "municipalidad": "|055",
    "biblioteca": "|045",
    "escuela": "|055",
    # culto y memoria
    "iglesia": "|505",
    "cementerio": "|303",
    "atraccion": "|515",
    # subsuelo e interiores
    "alcantarilla": "|113",
    "interior": "|333",
    "sala": "|333",
    "pasillo": "|222",
    "escalera": "|334",
    "sotano": "|112",
    "azotea": "|334",
    "muro": "|111",
}

COLOR_POR_DEFECTO = "|w"

# El jugador va en negro sobre amarillo: es lo único del mapa que tiene fondo,
# así que se encuentra de un vistazo sin importar sobre qué esté parado.
COLOR_JUGADOR = "|[550|000"


def aclarar(color):
    """
    Sube un punto cada componente de un color xterm256.

    Se usa para las puertas: la puerta es el mismo edificio, pero iluminada.
    Marcarla con un carácter propio obligaría a inventar un glifo por cada tipo
    de construcción; con el color alcanza y no se pierde de qué edificio es.

    """
    if len(color) == 4 and color[1:].isdigit():
        return "|" + "".join(str(min(5, int(c) + 2)) for c in color[1:])
    return color


def colorear(tipo, glifo, puerta=False):
    """Envuelve un carácter del mapa en el color de su tipo."""
    color = COLORES.get(tipo, COLOR_POR_DEFECTO)
    if puerta:
        color = aclarar(color)
    return f"{color}{glifo}|n"


def icono_de(tipo, vecinos=None):
    """
    Carácter con el que se dibuja una celda.

    Args:
        tipo (str): tipo de la celda.
        vecinos (tuple, optional): `(norte, sur, este, oeste)` con 1 donde
            sigue la trama. Solo lo usan las calles y avenidas.

    """
    if tipo in DIBUJO_TRAMA:
        if vecinos:
            return DIBUJO_TRAMA[tipo].get(tuple(vecinos), ICONO_DESCONOCIDO)
        return DIBUJO_TRAMA[tipo][(0, 0, 1, 1)]
    if tipo == "puente":
        return ICONO_PUENTE
    if tipo == "diagonal":
        return ICONO_DIAGONAL
    return ICONOS.get(tipo, ICONO_DESCONOCIDO)


def leyenda(tipos):
    """
    Arma las líneas de referencia para los tipos que aparecen en un mapa.

    Args:
        tipos (iterable): tipos presentes en lo que se está dibujando.

    Returns:
        list: líneas de texto, tres entradas por línea.

    """
    orden = list(GLIFOS_REFERENCIA) + list(ICONOS)
    presentes = [t for t in orden if t in set(tipos)]
    lineas = []
    for i in range(0, len(presentes), 3):
        tanda = presentes[i : i + 3]
        lineas.append(
            "  ".join(
                f"{COLORES.get(t, COLOR_POR_DEFECTO)}{_glifos(t):<3}|n "
                f"{NOMBRES.get(t, t):<15}"
                for t in tanda
            ).rstrip()
        )
    return lineas


def _glifos(tipo):
    """Los caracteres con que se dibuja un tipo, para la referencia."""
    return GLIFOS_REFERENCIA.get(tipo) or ICONOS.get(tipo, ICONO_DESCONOCIDO)
