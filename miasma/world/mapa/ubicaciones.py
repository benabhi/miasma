# -*- coding: utf-8 -*-
"""
La grilla de Nébrida: qué hay en cada celda de cada plano.

Cada plano se dibuja como una imagen de texto, un carácter por celda. Es la
forma más directa de garantizar lo que queremos: **una grilla densa, sin
huecos**. Si en el dibujo no queda un espacio en blanco, en el juego tampoco.

    y crece hacia el norte  ->  la primera línea de la imagen es la de arriba
    x crece hacia el este   ->  el primer carácter de cada línea es el oeste

Casi todos los caracteres son salas por las que se camina, y el constructor las
conecta automáticamente con sus vecinas ortogonales: no hay que declarar una
sola salida norte/sur/este/oeste a mano. Los tipos de `iconos.INTRANSITABLES`
—agua, arboleda, muro— se dibujan pero no son salas: son el borde del mundo, no
un agujero.

La ciudad tiene unas dos mil quinientas salas. Las que llevan nombre y
descripción propios están en `nebrida.py` y reclaman su celda en `NOMBRADAS`;
son los lugares singulares, dos docenas. Las demás las arma el constructor con
`RELLENO` y, si son calle, con el nombre de la calle que sale de `CALLES`. Una
ciudad no necesita dos mil descripciones distintas: necesita que cada esquina
sepa cómo se llama.
"""

# --------------------------------------------------------------------------
# Qué significa cada carácter de los dibujos
# --------------------------------------------------------------------------

LEYENDA = {
    "c": "calle",
    "a": "avenida",
    "D": "diagonal",
    "p": "puente",
    "v": "vereda",
    "z": "plaza",
    "q": "parque",
    "d": "descampado",
    "e": "edificio",
    "h": "casa",
    "s": "comercio",
    "m": "mercado",
    "g": "industria",
    "i": "iglesia",
    "H": "hospital",
    "P": "comisaria",
    "B": "bomberos",
    "E": "escuela",
    "L": "biblioteca",
    "A": "municipalidad",
    "U": "hotel",
    "X": "cementerio",
    "R": "estacion_tren",
    "&": "muelle",
    "!": "faro",
    "*": "atraccion",
    "V": "alcantarilla",
    "~": "agua",
    "T": "arbol",
    "#": "muro",
    "o": "interior",
    "-": "pasillo",
    "x": "escalera",
    "u": "sotano",
    "^": "azotea",
}

# --------------------------------------------------------------------------
# NÉBRIDA
#
# El lago al suroeste, el río bajando del norte y curvando al suroeste hasta
# desembocar en él, tres puentes, la ciudad a los dos lados y bosque en las
# afueras del norte y del este.
#
# La retícula tiene separaciones desparejas a propósito: manzanas de dos, tres
# y cuatro celdas mezcladas, más una diagonal que corta el damero. Una ciudad
# con todas las manzanas iguales se lee como papel cuadriculado.
# --------------------------------------------------------------------------

NEBRIDA = """
TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT~~~~~TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
TTTThhTTTTTTTTTTTTTTchTTTTTTTTTTTTTThcTTTTTTT~~~~~TThhTTTTTTTTTTTTTTggTTTTTTTTTT
TThchhhcTTTTThhTTThhchhhTTTTTahTTThhhchhTTTT~~~~~TchhhchTTTTTeeTTTgcgggcTTTTTTTT
hhhchhhchTTThhhhchhhchhhcTTThahhhchhhchhhTTT~~~~~hchhhDhhTTTeeecgggcgggcgTTTTTTT
cccccccccccccccccccccccccccccaccccccccccccc~~~~~cccccDccccacccccccccccccTTTTTTTT
hhhchhhchhhcsssscXXXcXXdchhhhahhhcssschhhcppppppphchDhchhhaEEEgcgggceeecssTTTTTT
hhhchhhchhhcsssscXXXcXXdcPPhhahhhcBBschhhc~~~~~hhhcDhhchhhaEEEgcgggceeecssTTTTTT
hhhchhhchhhcsssscXXXcXXdcPPhhahhhcBBschhhc~~~~~hhhDhhhchhhaEEEgcgggceeecsTTTTTTT
cccccccccccccccccccccccccccccaccccccccccc~~~~~cccDccccccccacccccccccccccccTTTTTT
dddchhhcssscddddchhhcssscddddassscdddchhh~~~~~HHDdchhhcsssaddddcgggcgggcTTTTTTTT
dddchhhcsssciiddczzhcssscddddassscdddchh~~~~~cHDHdchhhcsssaddddcgggcgggcggTTTTTT
dddchhhcsssciiddczzhcssscddddassscdddch~~~~~scDHHdchhhcsssaddddcgggcgggcgggTTTTT
cccccccccccccccccccccccccccccacccccccc~~~~~ccDccccccccccccaccccccccccccccTTTTTTT
sssceeecdddchhhhchhhchhhchhhhaeeecdddc~~~~~eDcHHHecsssceeeaqqqqcgggcgggcggTTTTTT
sssceeecdddchhhhchhhchhhchhhhaeeecddd~~~~~eDecHHHecsssceeeaqqqqczzzcgggcTTTTTTTT
cccccccccccccccccccccccccccccacccccpppppppDcccccccVcccccccaccccccccccccccTTTTTTT
hhhchhhchhhchhhhchhhcEEEchhhhaqqhch~~~~~eDzzzciiiecPPPcUUUaqqqqcgggcgggcgggTTTTT
hhhchhhczzhchhhhchhhcEEEchhhhaqqhc~~~~~hDczzzciiiecPPPcUUUaq*qqcgggcgggcggTTTTTT
hhhchhhczzhchhhhchhhcEEEchhhhaqqh~~~~~hDeczzzciiiecPPPcUUUaqqqqcgggcgggcgTTTTTTT
aaaaaaaaaaaaaaaaaaaaaaaaVaaaaaaa~~~~~aDaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaTTTTTTT
dddcssschhhchhhhceeechhhchhhhas~~~~~hDhhecAAAcLLLscBBBcmmmaggggcRRRcRRdcTTTTTTTT
dddcssschhhcshhhceeechhhchhhh~~~~~hhDchhecAAAcLLLscBBBcmmmaggggcRRRcRRdceeTTTTTT
cccccccccccccccccccccccccccc~~~~~ccDccccccccccccccccccccccacccccccccccccccTTTTTT
hhhcdddchhhchhhhcssschhhce~~~~~ddcDhhchheceeeceeeecsssceeeaeeeecgggcgggcgTTTTTTT
~~~cdddchhhchhhhcssschhpppppppdddDhhhchheceeeceeeecsssceeeaeeeeciiicgggcggTTTTTT
~~~~~ddchhhchhhhcdssc~~~~~eeeaddDchhhchheceeeceeeecsssceeeaeeeeciiicgggcTTTTTTTT
~~~~&&&cccccccccccc~~~~~cccccacDccccccccccccccccccccccccccacccccccccccccccTTTTTT
~~~~~~~~~sschhhh~~~~~dddchhhhaDhhcssschhhchhhcddddchhhceeeaggggcgggceeecsssTTTTT
~~~~~~~~~~schh~~~~~hczzdchhhhDqqqcssschhhchhhcddddchhhceeeaggggcgggceeecsTTTTTTT
~~~~~~~~~~~~~~~~~hhhczzdchhhDaqqqcssschhhchhhcddddchhhceeeaggggcgggceeecssTTTTTT
~~~~~~~~~~&&&ccccccccccccccDcaccccccccccccccccccccccccccccacccccccccccccTTTTTTTT
~~~~~~~~~~~~~~ggceeecgggceDeeaeeecgggceeecgggceeeecgggceeeaeeeecgggceeecgTTTTTTT
~~~~~~~~~~~~~~~gceeecgggcDeeeaeeecgggceeecgggceeeecgggceeeaeeeecgggceeecgggTTTTT
~~~~~~~~~~~~~&&&ccccccccDccccaccccccccccccccccccccccccccccacccccccccccccccTTTTTT
~~~~~~~~~~~~~~~~~gggcssscddddassscdddcgggcssscddddcgggcsssaggggcssscdddcgTTTTTTT
~~~~~~~~~~~~~~~~~~ggcssscddddassscdddcgggcssscddddcgggcsssaggggcssscdddcgTTTTTTT
~~~~~~~~~~~~~~~~~~~gcssscddddassscdddcgggcssscddddcgggcsssaggggcssscdddcTTTTTTTT
~~~~~~~~~~~~~~!&&&&ccccccccccaccccccccccccccccccccccccccccacccccccccccccccTTTTTT
~~~~~~~~~~~~~~~~~~~~cdddcggggahhhcsssceeecdddcggggcgggchhhaeeeecdddcgggcggTTTTTT
~~~~~~~~~~~~~~~~~~~~cdddcggggahhhcsssceeecdddcggggcgggchhhaeeeecdddcgggcgTTTTTTT
"""

# --------------------------------------------------------------------------
# Cómo se llama cada calle
#
# El constructor le pone a cada tramo de calle el nombre de la calle a la que
# pertenece, y a cada esquina el de las dos que se cruzan. Es lo que hace que
# caminar por la ciudad se sienta como caminar por una ciudad y no por una
# grilla: "Calle Undiano y Calle Rovira" ubica; "Calzada" no.
# --------------------------------------------------------------------------

CALLES = {
    # este-oeste, por fila
    "eo": {
        2: "Calle del Puerto",
        6: "Calle Almenara",
        9: "Calle Verdial",
        13: "Calle Ostrada",
        17: "Calle Sagrera",
        20: "Avenida Nébrida",
        24: "Calle Berlanga",
        27: "Calle Undiano",
        31: "Calle Marzal",
        35: "Calle del Cementerio",
    },
    # norte-sur, por columna
    "ns": {
        3: "Calle Arriaga",
        7: "Calle Zubieta",
        11: "Calle Olvera",
        16: "Calle Trévano",
        20: "Calle Cárcava",
        24: "Calle Solmena",
        29: "Avenida de los Alisos",
        33: "Calle Vilaña",
        37: "Calle Amézaga",
        41: "Calle Rovira",
        45: "Calle Bergara",
        50: "Calle Ochoa",
        54: "Calle Alduín",
        58: "Avenida del Río",
        63: "Calle Ferrán",
        67: "Calle Maruján",
        71: "Calle de los Galpones",
    },
}

# La diagonal no cae ni en una fila ni en una columna: tiene su propio nombre.
NOMBRE_DIAGONAL = "Diagonal Sur"

# --------------------------------------------------------------------------
# Los interiores, cada uno con su plano y sus niveles
# --------------------------------------------------------------------------

HOSPITAL_SOTANO = """
####
uu##
"""

HOSPITAL_PB = """
##o#
ooo#
#x##
"""

HOSPITAL_1 = """
---#
#-##
"""

HOSPITAL_2 = """
---#
#-##
"""

HOSPITAL_AZOTEA = """
^^^#
#^##
"""

CLOACAS = """
#v
#v
vv
#v
"""

PLANOS = {
    "nebrida": {"nombre": "Nébrida", "niveles": {0: NEBRIDA}},
    "hospital": {
        "nombre": "Hospital Municipal",
        "niveles": {
            -1: HOSPITAL_SOTANO,
            0: HOSPITAL_PB,
            1: HOSPITAL_1,
            2: HOSPITAL_2,
            3: HOSPITAL_AZOTEA,
        },
    },
    "cloacas": {"nombre": "Alcantarillas", "niveles": {-1: CLOACAS}},
}

NOMBRES_PLANO = {clave: spec["nombre"] for clave, spec in PLANOS.items()}

# --------------------------------------------------------------------------
# Qué sala con nombre propio ocupa cada celda
# --------------------------------------------------------------------------

NOMBRADAS = {
    # --- Nébrida ---
    "plaza_mayor": ("nebrida", 42, 21, 0),
    "municipalidad": ("nebrida", 42, 18, 0),
    "catedral": ("nebrida", 46, 21, 0),
    "biblioteca": ("nebrida", 46, 18, 0),
    "comisaria_central": ("nebrida", 51, 21, 0),
    "cuartel_bomberos": ("nebrida", 51, 18, 0),
    "mercado": ("nebrida", 55, 18, 0),
    "hospital_frente": ("nebrida", 46, 25, 0),
    "estacion_tren": ("nebrida", 64, 18, 0),
    "cementerio": ("nebrida", 17, 32, 0),
    "faro": ("nebrida", 14, 2, 0),
    "puente_mayor": ("nebrida", 35, 24, 0),
    "boca_alcantarilla": ("nebrida", 24, 20, 0),
    # --- Hospital Municipal ---
    "hos_farmacia": ("hospital", 0, 1, 0),
    "hos_recepcion": ("hospital", 1, 1, 0),
    "hos_guardia": ("hospital", 2, 1, 0),
    "hos_quirofano": ("hospital", 2, 2, 0),
    "hos_escalera": ("hospital", 1, 0, 0),
    "hos_generador": ("hospital", 0, 0, -1),
    "hos_morgue": ("hospital", 1, 0, -1),
    "hos_internacion_1": ("hospital", 1, 0, 1),
    "hos_internacion_2": ("hospital", 1, 0, 2),
    "hos_helipuerto": ("hospital", 1, 0, 3),
    # --- Alcantarillas ---
    "alc_pozo": ("cloacas", 1, 3, -1),
    "alc_colector": ("cloacas", 1, 2, -1),
    "alc_camara": ("cloacas", 1, 1, -1),
    "alc_oficina": ("cloacas", 0, 1, -1),
}

# Interiores de una sola sala, sin celda propia. Por ahora no hay: todo lo que
# se puede visitar ocupa su lugar en algún plano.
ANCLADAS = {}

# --------------------------------------------------------------------------
# Las celdas que no reclamó nadie
#
# Dos mil salas genéricas serían dos mil salas iguales, así que cada tipo tiene
# varias versiones y el constructor elige una según la coordenada: siempre la
# misma para la misma celda, distinta de la de al lado.
# --------------------------------------------------------------------------

RELLENO = {
    "calle": [
        ("Calzada", "Asfalto partido, un cordón que alguna vez fue blanco y la "
         "niebla cerrando el fondo a los diez metros."),
        ("Calzada", "Media calle levantada por una cuadrilla que no volvió a "
         "taparla. Las vallas siguen puestas, con sus luces naranjas."),
        ("Calzada", "Autos estacionados contra el cordón, en fila, todos con "
         "el parabrisas tapado de ceniza y ninguno chocado."),
        ("Calzada", "Un tramo con los plátanos podados en cubo a los dos "
         "lados. Las hojas caídas están negras y no crujen."),
    ],
    "avenida": [
        ("Avenida", "Dos manos separadas por un cantero central con árboles "
         "pelados. Es ancha, y esa anchura no tranquiliza: se ve poco y de "
         "lejos."),
        ("Avenida", "Cuatro carriles y una parada de colectivo con techo de "
         "chapa. En el banco hay una campera doblada con cuidado."),
        ("Avenida", "El cantero central tiene una hilera de faroles altos, "
         "todos encendidos, que no llegan a iluminar las veredas."),
    ],
    "diagonal": [
        ("Diagonal Sur", "La diagonal corta el damero en oblicuo y deja "
         "esquinas en punta, veredas triangulares y ochavas que no cierran "
         "con nada."),
        ("Diagonal Sur", "Un tramo en pendiente suave, con las baldosas "
         "puestas en espiga. Los edificios de los costados están cortados al "
         "sesgo."),
    ],
    "puente": [
        ("Puente", "Tablero de acero remachado sobre agua negra y quieta, con "
         "un pretil a cada lado y faroles cada diez metros."),
        ("Puente", "El tramo central, donde el río se ve mejor. No se oye "
         "correr el agua."),
    ],
    "vereda": [
        ("Vereda", "Baldosas flojas y ceniza acumulada contra el cordón."),
    ],
    "plaza": [
        ("Plaza", "Un cuadrado de baldosas con bancos de hierro, canteros de "
         "boj sin podar y una fuente que no corre."),
        ("Plaza", "Juegos de plaza: dos hamacas, un tobogán y un sube y baja, "
         "todo de caño pintado. Las hamacas se mueven."),
        ("Plaza", "Un solado en damero con una glorieta en el medio, de "
         "esas donde tocaba la banda municipal los domingos."),
    ],
    "parque": [
        ("Parque", "Césped alto hasta la rodilla, senderos de pedregullo y "
         "álamos en hilera. Acá la niebla se acuesta sobre el pasto."),
        ("Parque", "Una arboleda con bancos y tachos de basura con forma de "
         "animal. Alguien cortó el pasto de un solo cantero, hace poco."),
        ("Parque", "El sector del lago artificial: una cuenca de cemento "
         "vacía, con la baranda de troncos y un bote dado vuelta."),
    ],
    "descampado": [
        ("Baldío", "Terreno vacío entre construcciones: pasto quemado, "
         "escombros y un cerco de alambre caído."),
        ("Baldío", "Una obra parada. Los cimientos llenos de agua, el "
         "encofrado gris y una grúa fija que no gira."),
        ("Playón", "Cemento marcado con líneas amarillas descoloridas y unos "
         "pocos autos estacionados, prolijos, cubiertos de ceniza."),
    ],
    "casa": [
        ("Casa", "Una vivienda de dos plantas con el porche hundido y las "
         "cortinas corridas. La puerta del frente está abierta lo justo."),
        ("Casa", "Un chalet con jardín al frente, cerco vivo y un triciclo "
         "volcado en el camino de lajas."),
        ("Casa", "Casa chorizo de patio largo, con las macetas alineadas "
         "contra la pared y la ropa todavía tendida."),
        ("Casa", "Un PH de dos plantas con la escalera por afuera y cuatro "
         "medidores de luz en la entrada. Tres giran."),
    ],
    "edificio": [
        ("Edificio de departamentos", "Ocho pisos de ladrillo con balcones "
         "franceses y macetas muertas. El portero eléctrico tiene veinte "
         "timbres y ninguno anda."),
        ("Edificio de departamentos", "Un bloque de vivienda social, cuatro "
         "cuerpos alrededor de un patio interno con tendederos."),
        ("Edificio de oficinas", "Vidrio espejado del piso al techo, con el "
         "hall vacío y los molinetes de acceso destrabados."),
    ],
    "comercio": [
        ("Local a la calle", "Un negocio chico con la persiana a medio bajar "
         "y la vidriera empañada por dentro."),
        ("Almacén", "Góndolas hasta el techo y una heladera de bebidas que "
         "zumba. La caja registradora está abierta y llena."),
        ("Bar", "Doce mesas, barra de estaño y taburetes altos. En una mesa "
         "quedaron dos vasos servidos y sin tocar."),
        ("Farmacia", "Mostrador de vidrio, cajones numerados y la cruz verde "
         "de la puerta parpadeando."),
        ("Ferretería", "Todo colgado de ganchos y ordenado por tamaño, del "
         "clavo más chico a la maza."),
    ],
    "mercado": [
        ("Mercado Central — puestos", "Puestos de chapa y madera bajo la nave "
         "de hierro, cada uno con su toldo a rayas y su balanza."),
    ],
    "industria": [
        ("Galpón", "Chapa acanalada, portón corredizo y un muelle de carga a "
         "la altura de un camión. Huele a aceite quemado."),
        ("Depósito", "Estanterías industriales de tres alturas con pallets "
         "envueltos en film. Un autoelevador quedó cargado a mitad de camino."),
        ("Taller", "Fosa abierta en el piso, un elevador hidráulico a media "
         "altura sosteniendo nada, y las herramientas ordenadas por tamaño."),
    ],
    "iglesia": [
        ("Iglesia de barrio", "Nave única, doce bancos y un campanario corto. "
         "El vitral, desde adentro, se ve negro."),
    ],
    "hospital": [
        ("Hospital Municipal — predio", "Terreno del hospital: reja de "
         "lanzas, cantero de boj sin podar y carteles de circulación interna."),
    ],
    "comisaria": [
        ("Comisaría", "Ladrillo visto, dos escalones de granito y un farol "
         "azul sobre la puerta. El farol está prendido."),
    ],
    "bomberos": [
        ("Destacamento de bomberos", "Portón levantado, dársena vacía y los "
         "trajes de fuego colgados del techo por el casco."),
    ],
    "escuela": [
        ("Escuela", "Paredón de ladrillo de tres metros rematado con reja de "
         "puntas, y adentro un patio con el mástil sin bandera."),
        ("Escuela — aulas", "Aulas con los pupitres y las sillas levantadas "
         "sobre las mesas, como al final del día."),
    ],
    "biblioteca": [
        ("Biblioteca — depósito", "Estanterías compactas sobre rieles, con "
         "manivela. Huele a papel húmedo."),
    ],
    "municipalidad": [
        ("Municipalidad — oficinas", "Mostradores numerados, sillas de espera "
         "y un cartel de turnos parado en un número que no avanza."),
    ],
    "hotel": [
        ("Hotel", "Lobby con alfombra de guardas, sillones de cuero y un "
         "casillero de correspondencia con un sobre en cada casilla."),
    ],
    "cementerio": [
        ("Cementerio", "Lápidas en hileras, cipreses podados y senderos de "
         "grava que crujen más fuerte de lo que deberían."),
        ("Cementerio — panteones", "Bóvedas familiares de mármol con puertas "
         "de bronce y vidrios biselados. Algunas están abiertas."),
    ],
    "estacion_tren": [
        ("Estación — andenes", "Marquesina de chapa, bancos atornillados y "
         "vías que se pierden en la niebla a los treinta metros."),
        ("Estación — playa de maniobras", "Vías muertas, un vagón de carga "
         "abierto y un cambio de agujas trabado."),
    ],
    "muelle": [
        ("Muelle", "Tablones hinchados de humedad sobre el agua, con bitas de "
         "hierro y neumáticos colgando como defensas."),
    ],
    "faro": [
        ("Punta del faro", "Una punta de piedra que entra en el lago, con la "
         "torre blanca y roja girando su linterna."),
    ],
    "atraccion": [
        ("Calesita", "Plataforma circular bajo una carpa de rayas, con "
         "caballos de madera empalados en barras de bronce. Gira."),
    ],
    "alcantarilla": [
        ("Boca de tormenta", "Una tapa de hierro fundido corrida a un "
         "costado, con el escudo de la ciudad en relieve."),
    ],
    "interior": [("Sala", "Un ambiente cerrado, sin ventanas a la calle.")],
    "sala": [("Sala", "Un ambiente cerrado, sin ventanas a la calle.")],
    "pasillo": [
        ("Pasillo", "Piso encerado y la mitad de los tubos fluorescentes "
         "apagados."),
    ],
    "escalera": [
        ("Escalera", "Hormigón sin revestir, pasamanos de caño y una lámpara "
         "enjaulada en cada descanso."),
    ],
    "sotano": [
        ("Subsuelo", "Caños forrados, piso de rejilla y aire varios grados "
         "más frío."),
    ],
    "azotea": [
        ("Azotea", "Membrana asfáltica, maquinaria de ventilación y un "
         "parapeto bajo. Desde acá la niebla se ve desde arriba."),
    ],
}

# Tipos de relleno que son de exterior: les corresponde el párrafo de niebla.
RELLENO_EXTERIOR = frozenset(
    (
        "calle", "avenida", "diagonal", "puente", "vereda", "plaza", "parque",
        "descampado", "cementerio", "muelle", "faro", "atraccion", "azotea",
        "estacion_tren", "alcantarilla", "hospital", "escuela",
    )
)


# --------------------------------------------------------------------------
# Las puertas
#
# Un edificio no es un terreno por el que se pasa. De cada grupo de celdas
# contiguas del mismo tipo, el constructor hace sala **solo la celda de la
# puerta** y la conecta con la calle mediante `entrar` / `salir`; el resto del
# edificio se dibuja pero es macizo, y desde la calle no hay salida hacia él.
#
# Todavía no hay interiores —eso viene después—, así que la sala de la puerta
# es el zaguán: el umbral desde donde algún día se sigue.
# --------------------------------------------------------------------------

ENTRADAS = {
    "edificio": (
        "Portal de un edificio",
        "Un zaguán de baldosa calcárea con la puerta de calle trabada abierta, "
        "el tablero de timbres a un lado y la escalera arrancando al fondo.\n\n"
        "La escalera sube a oscuras. Todavía no hay por dónde seguir.",
    ),
    "casa": (
        "Puerta de una casa",
        "El porche de una vivienda: tres escalones, un felpudo y la puerta "
        "entornada.\n\n"
        "Adentro está oscuro y no se distingue nada.",
    ),
    "comercio": (
        "Puerta de un local",
        "El acceso de un negocio a la calle, con la persiana a medio bajar y el "
        "olor a encierro que sale de adentro.\n\n"
        "Habría que agacharse para pasar, y del otro lado no se ve.",
    ),
    "mercado": (
        "Portón del mercado",
        "Uno de los portones de hierro del mercado, con las hojas plegadas "
        "contra la pared.\n\n"
        "Desde el umbral se oyen las cámaras de frío, más adentro.",
    ),
    "industria": (
        "Portón de un galpón",
        "Un portón corredizo de chapa sobre riel, abierto lo justo para que "
        "pase una persona de costado.\n\n"
        "Adentro huele a aceite quemado y no entra luz.",
    ),
    "iglesia": (
        "Atrio de una iglesia",
        "Tres escalones de piedra y las puertas dobles de madera, cerradas pero "
        "sin traba.\n\n"
        "Del otro lado se filtra olor a cera.",
    ),
    "hospital": (
        "Acceso del hospital",
        "Una puerta de servicio del predio, con el cartel de circulación "
        "interna y el timbre de guardia.\n\n"
        "Está cerrada.",
    ),
    "comisaria": (
        "Entrada de la comisaría",
        "Dos escalones de granito y una puerta de doble hoja bajo el farol "
        "azul.\n\n"
        "El farol está prendido. La puerta, no tanto.",
    ),
    "bomberos": (
        "Portón del cuartel",
        "El portón de la dársena, levantado hasta la mitad, con la marca de las "
        "ruedas todavía en el piso.\n\n"
        "Adentro está oscuro.",
    ),
    "escuela": (
        "Portón de la escuela",
        "El portón de reja del paredón perimetral, entreabierto lo justo para "
        "que pase una persona.\n\n"
        "Del otro lado, el patio, y más allá el edificio cerrado.",
    ),
    "biblioteca": (
        "Puerta de la biblioteca",
        "Una puerta de roble con vidrio repartido y el horario de atención "
        "pegado por dentro.\n\n"
        "El horario es de un día que ya pasó.",
    ),
    "municipalidad": (
        "Puerta lateral de la municipalidad",
        "Un acceso de empleados, con lector de tarjetas y un cenicero de pie "
        "todavía lleno.\n\n"
        "El lector tiene la luz roja.",
    ),
    "hotel": (
        "Entrada del hotel",
        "Puerta giratoria bajo una marquesina de luces de globo, la mitad "
        "fundidas.\n\n"
        "La puerta gira sola, despacio.",
    ),
    "estacion_tren": (
        "Acceso a los andenes",
        "Un pasaje con molinetes destrabados y carteles de destino colgando del "
        "techo.\n\n"
        "Más allá no se ve.",
    ),
}


# --------------------------------------------------------------------------
# Lectura de los dibujos
# --------------------------------------------------------------------------


def celdas_de(plano, z):
    """Convierte el dibujo de un nivel en un diccionario `{(x, y): tipo}`."""
    dibujo = PLANOS[plano]["niveles"][z]
    filas = dibujo.strip("\n").splitlines()
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


def nombre_de_calle(x, y):
    """
    Cómo se llama el tramo de calle en esa celda.

    En una esquina se nombran las dos calles que se cruzan, que es como se
    ubica la gente en una ciudad de damero.

    """
    eo = CALLES["eo"].get(y)
    ns = CALLES["ns"].get(x)
    if eo and ns:
        return f"{eo} y {ns}"
    return eo or ns or None
