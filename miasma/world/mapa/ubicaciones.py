# -*- coding: utf-8 -*-
"""
La grilla del mundo: qué hay en cada celda de cada plano.

Cada plano se dibuja como una imagen de texto, un carácter por celda. Es la
forma más directa de garantizar lo que queremos: **una grilla densa, sin
huecos**. Si en el dibujo no queda un espacio en blanco, en el juego tampoco.

    y crece hacia el norte  ->  la primera línea de la imagen es la de arriba
    x crece hacia el este   ->  el primer carácter de cada línea es el oeste

Casi todos los caracteres son salas por las que se camina, y el constructor las
conecta automáticamente con sus vecinas ortogonales: no hay que declarar una
sola salida norte/sur/este/oeste a mano. Los tipos de `iconos.INTRANSITABLES`
—agua, arboleda, muro— se dibujan pero no son salas: son el borde del mundo,
no un agujero.

Las salas con nombre y descripción propios (las de `silent_hill.py`) reclaman
su celda en `NOMBRADAS`. Las demás celdas las llena el constructor con salas
genéricas según su tipo, para que el pueblo sea caminable de punta a punta sin
tener que escribir doscientas descripciones.

`ANCLADAS` son los interiores de una sola sala. No ocupan celda: dibujar un
mapa de 1×1 para el interior de un bar no le sirve a nadie, así que cuando el
jugador está adentro se dibuja la calle de la que entró.
"""

# --------------------------------------------------------------------------
# Qué significa cada carácter de los dibujos
# --------------------------------------------------------------------------

LEYENDA = {
    "c": "calle",
    "x": "cruce",
    "a": "avenida",
    "v": "vereda",
    "p": "puente",
    "l": "callejon",
    "d": "descampado",
    "e": "edificio",
    "h": "casa",
    "s": "comercio",
    "i": "iglesia",
    "E": "escuela",
    "H": "hospital",
    "P": "comisaria",
    "M": "hotel",
    "g": "industria",
    "o": "interior",
    "-": "pasillo",
    "X": "escalera",
    "u": "sotano",
    "^": "azotea",
    "*": "atraccion",
    "&": "muelle",
    "!": "faro",
    "V": "alcantarilla",
    "~": "agua",
    "T": "arbol",
    "#": "muro",
}

# --------------------------------------------------------------------------
# EL PUEBLO
#
# Old Silent Hill al noroeste, el canal en el medio con el puente levadizo, el
# centro al este y el área turística bajando hacia el lago Toluca. Un solo
# plano continuo: se camina de punta a punta.
#
#       x  0 1 2 3 4 5 6 7 8 9 10
# --------------------------------------------------------------------------

# El pueblo es una retícula de calles con manzanas de 2x2: hay calle cada
# tres celdas en los dos ejes, y lo que queda entre ellas son las manzanas.
# Ese patrón es lo que hace que el mapa se lea como una ciudad y no como una
# lista de cruces sueltos.
#
#   Old Silent Hill   x 0..9   y 12..21   calles en x 0,3,6,9  y 12,15,18,21
#   canal             x 10..11            con el puente levadizo en y 12
#   Central           x 12..18 y 12..21   calles en x 12,15,18  y 12,15,18,21
#   área turística    x 12..18 y 0..11    calles en x 12,15,18  y 0,3,6,9
#   lago Toluca       x 0..11  y 0..11
#
# Bachman Road (x 9 y x 18) es la arteria: cruza el pueblo entero.
PUEBLO = """
TTTTTTTTTd~~TTTTTTTT
xccxccxcca~~xccxccaT
chhchhcssa~~cPPcssaT
chhchhcdda~~cPPcseaT
xccxccxcca~~xccxccaT
chhchhcssa~~csscHHaT
chlchdcgga~~csdcHHaT
xccxccxcca~~xccxccaT
csscEEciga~~ceeceeaT
csdcEEciga~~ceeceeaT
xccxccxccappxccVccaT
~~~~~~~~~~~~ceecMMaT
~~~~~~~~~~~~ceecMMaT
~~~~~~~~~~~~xccxcca*
~~~~~~~~~~~~chhcssaT
~~~~~~~~~~~~chhcssaT
~~~~~~~~~~~pxccxccaT
~~~~~~~~~~~~csdcsMaT
~~~~~~~~~~~~csdcMMaT
~~~~~~~~~~~!xccxccaT
~~~~~~~~~~~~cddcddaT
~~~~~~~~~~~~cddcddaT
~~~~~~~~~~~&xccxccaT
"""

ESCUELA_PB = """
---
-d-
#o#
#c#
"""

ESCUELA_1P = """
o-#
-o#
o##
###
"""

ESCUELA_AZOTEA = """
###
^##
###
###
"""

ESCUELA_SOTANO = """
###
u##
###
###
"""

HOSPITAL_PB = """
###o
oooo
ooo#
#cX#
"""

HOSPITAL_1 = """
####
####
####
##-#
"""

HOSPITAL_2 = """
####
####
####
##-#
"""

HOSPITAL_SOTANO = """
####
####
#X##
####
"""

HOSPITAL_MAQUINAS = """
####
####
#u##
####
"""

CLOACAS = """
#X
#V
oV
#V
#X
"""

CLOACAS_ALTO = """
##
##
#V
##
##
"""

PARQUE = """
T*T
*d*
TTT
"""

# plano -> {nivel z: dibujo}
PLANOS = {
    "pueblo": {"nombre": "Silent Hill", "niveles": {0: PUEBLO}},
    "escuela": {
        "nombre": "Escuela Midwich",
        "niveles": {
            -1: ESCUELA_SOTANO,
            0: ESCUELA_PB,
            1: ESCUELA_1P,
            2: ESCUELA_AZOTEA,
        },
    },
    "hospital": {
        "nombre": "Hospital Alchemilla",
        "niveles": {
            -2: HOSPITAL_MAQUINAS,
            -1: HOSPITAL_SOTANO,
            0: HOSPITAL_PB,
            1: HOSPITAL_1,
            2: HOSPITAL_2,
        },
    },
    "cloacas": {
        "nombre": "Alcantarillas",
        "niveles": {-1: CLOACAS, 0: CLOACAS_ALTO},
    },
    "parque": {"nombre": "Lakeside Amusement Park", "niveles": {0: PARQUE}},
}

NOMBRES_PLANO = {clave: spec["nombre"] for clave, spec in PLANOS.items()}

# --------------------------------------------------------------------------
# Qué sala con nombre propio ocupa cada celda
# --------------------------------------------------------------------------

NOMBRADAS = {
    # --- Old Silent Hill: cruces -------------------------------------------
    #     Bradbury x0 · Midwich x3 · Levin x6 · Bachman x9
    #     Bloch y12 · Ellroy y15 · Matheson y18 · Finney y21
    "osh_finney_bradbury": ("pueblo", 0, 21, 0),
    "osh_finney_midwich": ("pueblo", 3, 21, 0),
    "osh_finney_levin": ("pueblo", 6, 21, 0),
    "osh_finney_bachman": ("pueblo", 9, 21, 0),
    "osh_matheson_bradbury": ("pueblo", 0, 18, 0),
    "osh_matheson_midwich": ("pueblo", 3, 18, 0),
    "osh_matheson_levin": ("pueblo", 6, 18, 0),
    "osh_matheson_bachman": ("pueblo", 9, 18, 0),
    "osh_ellroy_bradbury": ("pueblo", 0, 15, 0),
    "osh_ellroy_midwich": ("pueblo", 3, 15, 0),
    "osh_ellroy_levin": ("pueblo", 6, 15, 0),
    "osh_ellroy_bachman": ("pueblo", 9, 15, 0),
    "osh_bloch_bradbury": ("pueblo", 0, 12, 0),
    "osh_bloch_midwich": ("pueblo", 3, 12, 0),
    "osh_bloch_levin": ("pueblo", 6, 12, 0),
    "osh_bloch_bachman": ("pueblo", 9, 12, 0),
    "osh_bachman_norte": ("pueblo", 9, 22, 0),
    "osh_callejon_basket": ("pueblo", 8, 19, 0),
    "osh_callejon_gordon": ("pueblo", 2, 16, 0),
    "osh_puente_levadizo": ("pueblo", 10, 12, 0),
    # --- Old Silent Hill: lo que hay en las manzanas -----------------------
    "int_cafe_5to2": ("pueblo", 8, 20, 0),
    "int_tienda": ("pueblo", 7, 20, 0),
    "int_queen_burger": ("pueblo", 8, 17, 0),
    "int_casa_levin": ("pueblo", 5, 17, 0),
    "int_casa_gordon": ("pueblo", 1, 16, 0),
    "int_iglesia_balkan": ("pueblo", 7, 13, 0),
    "int_cut_rite": ("pueblo", 1, 13, 0),
    "int_estacion_servicio": ("pueblo", 8, 16, 0),
    # --- Central Silent Hill -----------------------------------------------
    #     Simmons x12 · Sagan x15 · Bachman x18
    #     Katz y12 · Munson y15 · Koontz y18 · Crichton y21
    "csh_cabecera_puente": ("pueblo", 11, 12, 0),
    "csh_crichton_simmons": ("pueblo", 12, 21, 0),
    "csh_crichton_sagan": ("pueblo", 15, 21, 0),
    "csh_crichton_bachman": ("pueblo", 18, 21, 0),
    "csh_koontz_simmons": ("pueblo", 12, 18, 0),
    "csh_koontz_sagan": ("pueblo", 15, 18, 0),
    "csh_koontz_bachman": ("pueblo", 18, 18, 0),
    "csh_munson_simmons": ("pueblo", 12, 15, 0),
    "csh_munson_sagan": ("pueblo", 15, 15, 0),
    "csh_munson_bachman": ("pueblo", 18, 15, 0),
    "csh_katz_simmons": ("pueblo", 12, 12, 0),
    "csh_katz_sagan": ("pueblo", 15, 12, 0),
    "csh_katz_bachman": ("pueblo", 18, 12, 0),
    "int_comisaria": ("pueblo", 14, 20, 0),
    "int_green_lion": ("pueblo", 17, 20, 0),
    "int_cafe_sun": ("pueblo", 13, 17, 0),
    "int_town_center": ("pueblo", 13, 14, 0),
    # --- Área turística ----------------------------------------------------
    #     Sandford x12 · Nathan Ave x15 · Bachman x18
    "res_bachman": ("pueblo", 18, 11, 0),
    "res_craig": ("pueblo", 18, 9, 0),
    "res_weaver": ("pueblo", 18, 6, 0),
    "res_nathan": ("pueblo", 15, 6, 0),
    "res_bartlett": ("pueblo", 15, 3, 0),
    "res_sandford": ("pueblo", 12, 3, 0),
    "res_muelle": ("pueblo", 11, 0, 0),
    "res_faro": ("pueblo", 11, 3, 0),
    "res_puente_sandford": ("pueblo", 11, 6, 0),
    "res_entrada_parque": ("pueblo", 19, 9, 0),
    "int_annies_bar": ("pueblo", 17, 8, 0),
    "int_bowl_o_rama": ("pueblo", 16, 8, 0),
    "int_indian_runner": ("pueblo", 13, 5, 0),
    "int_motel_recepcion": ("pueblo", 17, 5, 0),
    "int_hotel_lakeview": ("pueblo", 16, 11, 0),
    # --- Escuela Midwich ---------------------------------------------------
    "esc_entrada": ("escuela", 1, 0, 0),
    "esc_recepcion": ("escuela", 1, 1, 0),
    "esc_patio": ("escuela", 1, 2, 0),
    "esc_pasillo_pb_izq": ("escuela", 0, 2, 0),
    "esc_pasillo_pb_der": ("escuela", 2, 2, 0),
    "esc_caldera": ("escuela", 0, 2, -1),
    "esc_pasillo_1p_izq": ("escuela", 0, 2, 1),
    "esc_lab_quimica": ("escuela", 1, 2, 1),
    "esc_sala_musica": ("escuela", 0, 1, 1),
    "esc_biblioteca": ("escuela", 0, 3, 1),
    "esc_azotea": ("escuela", 0, 2, 2),
    # --- Hospital Alchemilla -----------------------------------------------
    "hos_patio": ("hospital", 1, 0, 0),
    "hos_ascensor": ("hospital", 2, 0, 0),
    "hos_oficina": ("hospital", 0, 1, 0),
    "hos_recepcion": ("hospital", 1, 1, 0),
    "hos_examen": ("hospital", 2, 1, 0),
    "hos_direccion": ("hospital", 0, 2, 0),
    "hos_cocina": ("hospital", 1, 2, 0),
    "hos_farmacia": ("hospital", 2, 2, 0),
    "hos_consultorio": ("hospital", 3, 2, 0),
    "hos_reuniones": ("hospital", 3, 3, 0),
    "hos_pasillo_2": ("hospital", 2, 0, 1),
    "hos_pasillo_3": ("hospital", 2, 0, 2),
    "hos_escalera_sotano": ("hospital", 1, 1, -1),
    "hos_generador": ("hospital", 1, 1, -2),
    # --- Alcantarillas -----------------------------------------------------
    "alc_entrada": ("cloacas", 1, 4, -1),
    "alc_tunel_norte": ("cloacas", 1, 3, -1),
    "alc_cruce": ("cloacas", 1, 2, -1),
    "alc_oficina": ("cloacas", 0, 2, -1),
    "alc_tunel_sur": ("cloacas", 1, 1, -1),
    "alc_salida": ("cloacas", 1, 0, -1),
    "alc_nivel_superior": ("cloacas", 1, 2, 0),
    # --- Lakeside Amusement Park -------------------------------------------
    "par_calesita": ("parque", 1, 2, 0),
    "par_montana_rusa": ("parque", 0, 1, 0),
    "par_explanada": ("parque", 1, 1, 0),
    "par_vuelta_al_mundo": ("parque", 2, 1, 0),
}

# --------------------------------------------------------------------------
# Interiores de una sola sala, sin celda propia
# --------------------------------------------------------------------------

ANCLADAS = {
    "osh_torre_control": "industria",
    "int_motel_hab3": "interior",
    "int_motel_garage": "industria",
    "esc_enfermeria": "sala",
    "esc_aula_pb": "sala",
    "esc_torre_reloj": "interior",
    "esc_reserva": "sala",
    "par_heladeria": "comercio",
}

# --------------------------------------------------------------------------
# Las celdas que no reclamó nadie: salas genéricas según su tipo.
#
# Rellenan la grilla para que se pueda caminar por todos lados sin escribir
# doscientas descripciones a mano. Son deliberadamente sobrias: el detalle está
# en las salas con nombre.
# --------------------------------------------------------------------------

RELLENO = {
    "calle": (
        "Calzada",
        "Un tramo de calle entre dos esquinas. Asfalto partido, un cordón que "
        "en algún momento fue blanco, y la niebla cerrando el fondo a los diez "
        "metros.",
    ),
    "cruce": (
        "Cruce",
        "Cuatro esquinas iguales, sin cartel que diga cuál es cuál. El "
        "semáforo cuelga apagado.",
    ),
    "avenida": (
        "Avenida",
        "Dos manos separadas por un cantero central con árboles pelados. Es "
        "ancha, y esa anchura no tranquiliza: se ve poco y de lejos.",
    ),
    "vereda": (
        "Vereda",
        "Un tramo de vereda ancha, de las que se hicieron pensando en gente "
        "paseando. Baldosas flojas y ceniza acumulada contra el cordón.",
    ),
    "callejon": (
        "Callejón",
        "Dos metros de ancho entre medianeras, con contenedores y cables de "
        "ropa cruzando arriba. Acá la niebla se queda quieta.",
    ),
    "descampado": (
        "Baldío",
        "Terreno vacío entre construcciones: pasto quemado, escombros y un "
        "cerco de alambre caído. Alguien apiló ladrillos, hace tiempo.",
    ),
    "casa": (
        "Casa abandonada",
        "Una vivienda de tablas con el porche hundido y las cortinas corridas. "
        "La puerta del frente está abierta lo justo para que entre el aire.",
    ),
    "edificio": (
        "Edificio de departamentos",
        "Cuatro pisos de ladrillo con balcones franceses y macetas muertas. El "
        "portero eléctrico tiene doce timbres y ninguno anda.",
    ),
    "comercio": (
        "Local a la calle",
        "Un negocio chico con la persiana a medio bajar y la vidriera "
        "empañada por dentro. El cartel perdió la mitad de las letras.",
    ),
    "industria": (
        "Galpón",
        "Chapa acanalada, portón corredizo y un muelle de carga a la altura de "
        "un camión. Huele a aceite quemado.",
    ),
    "escuela": (
        "Paredón de la escuela",
        "El muro perimetral de la Escuela Midwich: ladrillo, tres metros, "
        "rematado con una reja de puntas.",
    ),
    "pasillo": (
        "Pasillo",
        "Un tramo de pasillo con piso encerado y la mitad de los tubos "
        "fluorescentes apagados.",
    ),
    "interior": (
        "Sala",
        "Un ambiente cerrado, sin ventanas a la calle.",
    ),
    "azotea": (
        "Azotea",
        "Membrana asfáltica, maquinaria de ventilación y un parapeto bajo. "
        "Desde acá se ve niebla en todas las direcciones.",
    ),
    "sotano": (
        "Subsuelo",
        "Hormigón sin revestir, caños forrados y una lámpara enjaulada cada "
        "varios metros.",
    ),
    "atraccion": (
        "Atracción del parque",
        "Una estructura de hierro pintado, con la cola de acceso marcada por "
        "vallas cromadas. Sigue funcionando, sola.",
    ),
    "alcantarilla": (
        "Galería",
        "Un caño de sección ovalada por el que se camina erguido, con una "
        "banquina de cemento a cada lado del canal.",
    ),
    "puente": (
        "Puente",
        "Tablero de acero remachado sobre agua negra y quieta.",
    ),
    "muelle": (
        "Muelle",
        "Tablones hinchados de humedad sobre el agua, con bitas de hierro y "
        "neumáticos colgando como defensas.",
    ),
    "iglesia": (
        "Atrio",
        "El terreno de la iglesia: piedra gris, un cerco bajo de hierro y "
        "canteros con la tierra revuelta.",
    ),
    "hospital": (
        "Predio del hospital",
        "Terreno del Hospital Alchemilla: reja de lanzas, cantero de boj sin "
        "podar y la rampa de ambulancias vacía.",
    ),
    "comisaria": (
        "Frente de la comisaría",
        "Ladrillo visto, dos escalones de granito y un farol azul sobre la "
        "puerta. El farol está prendido.",
    ),
    "hotel": (
        "Explanada del hotel",
        "Una playa de estacionamiento en pendiente, con una marquesina de "
        "luces de globo. La mitad están fundidas.",
    ),
    "faro": (
        "Punta del faro",
        "Una punta de piedra que entra en el lago. La torre blanca y roja gira "
        "su linterna cada doce segundos y no ilumina nada.",
    ),
    "escalera": (
        "Escalera",
        "Hormigón sin revestir, pasamanos de caño pintado y una lámpara "
        "enjaulada en cada descanso.",
    ),
    "estacionamiento": (
        "Playón",
        "Cemento marcado con líneas amarillas descoloridas y unos pocos autos "
        "estacionados prolijamente, cubiertos de ceniza.",
    ),
}

# Tipos de relleno que son de exterior: les corresponde el párrafo de niebla.
RELLENO_EXTERIOR = frozenset(
    (
        "calle",
        "cruce",
        "avenida",
        "vereda",
        "callejon",
        "descampado",
        "puente",
        "muelle",
        "azotea",
        "atraccion",
        "iglesia",
        "hospital",
        "comisaria",
        "hotel",
        "faro",
        "estacionamiento",
    )
)


# --------------------------------------------------------------------------
# Lectura de los dibujos
# --------------------------------------------------------------------------


def celdas_de(plano, z):
    """
    Convierte el dibujo de un nivel en un diccionario `{(x, y): tipo}`.

    Args:
        plano (str): clave del plano.
        z (int): nivel.

    Returns:
        dict: tipo de cada celda, incluidas las intransitables.

    """
    dibujo = PLANOS[plano]["niveles"][z]
    filas = [f for f in dibujo.strip("\n").splitlines()]
    alto = len(filas)
    celdas = {}
    for indice, fila in enumerate(filas):
        y = alto - 1 - indice  # la primera línea es la de más al norte
        for x, caracter in enumerate(fila):
            if caracter == " ":
                continue
            tipo = LEYENDA.get(caracter)
            if tipo is None:
                raise ValueError(
                    f"plano '{plano}' nivel {z}: el carácter {caracter!r} en "
                    f"({x}, {y}) no está en LEYENDA"
                )
            celdas[(x, y)] = tipo
    return celdas


def todas_las_celdas():
    """Devuelve `{(plano, x, y, z): tipo}` para todos los planos y niveles."""
    todo = {}
    for plano, spec in PLANOS.items():
        for z in spec["niveles"]:
            for (x, y), tipo in celdas_de(plano, z).items():
                todo[(plano, x, y, z)] = tipo
    return todo
