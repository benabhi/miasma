# -*- coding: utf-8 -*-
"""
Los textos de Nébrida.

Acá van los nombres, las descripciones y las conexiones que **no** son de
grilla. La geometría —qué hay en cada celda y dónde cae cada cosa— está en
`ubicaciones.py`.

La ciudad es grande: unas dos mil salas. Escribir dos mil descripciones a mano
no tiene sentido y tampoco haría un mundo mejor, así que la mayoría de las
salas las arma el constructor a partir del tipo de celda y del nombre de la
calle (ver `RELLENO` y `CALLES` en `ubicaciones.py`). En `SALAS` van solamente
los lugares singulares: los que tienen que decir algo que ninguna otra sala
dice.
"""

# --------------------------------------------------------------------------
# Direcciones y sus alias
# --------------------------------------------------------------------------

DIRECCIONES = {
    "norte": ("n",),
    "sur": ("s",),
    "este": ("e",),
    "oeste": ("o",),
    "noreste": ("ne",),
    "noroeste": ("no",),
    "sureste": ("se",),
    "suroeste": ("so",),
    "arriba": ("ar", "subir"),
    "abajo": ("ab", "bajar"),
    "dentro": ("adentro", "entrar"),
    "fuera": ("afuera", "salir"),
}

OPUESTOS = {
    "norte": "sur",
    "sur": "norte",
    "este": "oeste",
    "oeste": "este",
    "noreste": "suroeste",
    "suroeste": "noreste",
    "noroeste": "sureste",
    "sureste": "noroeste",
    "arriba": "abajo",
    "abajo": "arriba",
    "dentro": "fuera",
    "fuera": "dentro",
}

SALA_INICIO = "plaza_mayor"

# La niebla es la constante del pueblo. Se antepone a las descripciones de
# exterior para no repetirla a mano en cada sala.
NIEBLA = (
    "|xLa niebla lo come todo a diez metros. Cae ceniza, mansa, como nieve "
    "sucia.|n\n\n"
)

SALAS = {}

# ==========================================================================
# EL CENTRO
# ==========================================================================

SALAS.update({
    "plaza_mayor": {
        "nombre": "Plaza Mayor",
        "exterior": True,
        "desc": (
            "El centro de Nébrida, y se nota: cuatro hileras de plátanos "
            "podados en cubo, bancos de hierro fundido y una fuente circular "
            "en el medio, seca, con el fondo tapizado de monedas y hojas "
            "negras.\n\n"
            "En el mástil no hay bandera. Sobre el pedestal donde debería "
            "haber una estatua hay dos botas de bronce cortadas a la altura "
            "del tobillo, y nada más.\n\n"
            "Alrededor, la ciudad: la municipalidad al norte, la catedral al "
            "este, y el resto de Nébrida abriéndose en todas las direcciones."
        ),
    },
    "catedral": {
        "nombre": "Catedral de Nébrida — nave central",
        "exterior": False,
        "desc": (
            "Tres naves de piedra gris bajo bóvedas de crucería, más altas de "
            "lo que el edificio prometía desde afuera. La luz entra por un "
            "rosetón que desde adentro se ve negro.\n\n"
            "Los bancos están corridos contra las paredes, despejando el "
            "centro. En el piso, sobre las lajas, alguien dibujó con tiza un "
            "círculo de cuatro metros y lo llenó de nombres.\n\n"
            "Las velas del altar están encendidas. Alguien las repone."
        ),
    },
    "municipalidad": {
        "nombre": "Municipalidad — hall de entrada",
        "exterior": False,
        "desc": (
            "Mármol, columnas y una escalera imperial que sube a un entrepiso "
            "de oficinas. En la pared del fondo, un mural de 1948 muestra a "
            "los fundadores de Nébrida repartiendo trigo.\n\n"
            "Al mural le arrancaron las caras. Todas, con cuidado, sin tocar "
            "el resto de la pintura."
        ),
    },
    "biblioteca": {
        "nombre": "Biblioteca Municipal",
        "exterior": False,
        "desc": (
            "Dos plantas de estanterías de roble alrededor de un vacío "
            "central, con mesas de lectura y lámparas de pantalla verde. Huele "
            "a papel y a humedad.\n\n"
            "El fichero está abierto en la letra N y le falta un cajón "
            "entero. Sobre el mostrador, una pila de libros con un cartel: "
            "|xRESERVADOS — NO PRESTAR|n. Son todos el mismo libro."
        ),
    },
    "mercado": {
        "nombre": "Mercado Central",
        "exterior": False,
        "desc": (
            "Una nave de hierro y vidrio con cuarenta puestos en dos hileras, "
            "cada uno con su toldo a rayas y su balanza. Las cámaras de frío "
            "del fondo siguen funcionando.\n\n"
            "En los cajones hay fruta perfecta, ordenada con el mejor lado "
            "hacia afuera, sin una sola marca. Nada se pudrió."
        ),
    },
    "hospital_frente": {
        "nombre": "Hospital Municipal — patio de ambulancias",
        "exterior": True,
        "desc": (
            "Una rampa de cemento bajo una marquesina, con lugar para tres "
            "ambulancias y ninguna estacionada. El cartel de |xGUARDIA|n sigue "
            "encendido en rojo sobre las puertas automáticas.\n\n"
            "Las puertas se abren solas cuando te acercás. Después se cierran."
        ),
    },
    "comisaria_central": {
        "nombre": "Comisaría Primera",
        "exterior": False,
        "desc": (
            "Mostrador de atención con vidrio blindado y un pasapapeles de "
            "acero. Detrás, escritorios con las computadoras encendidas y "
            "expedientes abiertos por la mitad.\n\n"
            "En el corcho hay treinta fotos de personas desaparecidas. "
            "Veintinueve están tachadas con una cruz roja. La que falta está "
            "en el centro, con un círculo."
        ),
    },
    "cuartel_bomberos": {
        "nombre": "Cuartel de Bomberos",
        "exterior": False,
        "desc": (
            "Un galpón de dos autobombas con el portón levantado y las dos "
            "dársenas vacías. Del techo cuelgan los trajes de fuego, "
            "colgados por el casco, como ahorcados prolijos.\n\n"
            "El caño de bajada rápida baja desde el entrepiso. Está tibio."
        ),
    },
})

# ==========================================================================
# LOS BORDES
# ==========================================================================

SALAS.update({
    "faro": {
        "nombre": "El faro",
        "exterior": True,
        "desc": (
            "Una torre blanca y roja de doce metros sobre una punta de piedra "
            "que entra en el lago. La puerta de hierro está soldada por el "
            "óxido.\n\n"
            "La linterna gira. Cada doce segundos el haz barre la niebla y no "
            "ilumina absolutamente nada."
        ),
    },
    "estacion_tren": {
        "nombre": "Estación Nébrida — andén 1",
        "exterior": True,
        "desc": (
            "Un andén de doscientos metros bajo una marquesina de chapa "
            "acanalada, con bancos de madera atornillados y carteles de "
            "destinos que ya no significan nada.\n\n"
            "El tablero de salidas marca un tren para dentro de cuatro "
            "minutos. Marca eso hace días."
        ),
    },
    "cementerio": {
        "nombre": "Cementerio del Norte",
        "exterior": True,
        "desc": (
            "Cuatro hectáreas de lápidas en hileras, cipreses podados y "
            "senderos de grava. El portón de hierro está abierto de par en "
            "par.\n\n"
            "La tierra de varias tumbas está removida. Desde adentro."
        ),
    },
    "puente_mayor": {
        "nombre": "Puente Mayor",
        "exterior": True,
        "desc": (
            "El más viejo de los tres puentes de Nébrida: cinco arcos de "
            "piedra sobre el río, con faroles de fundición cada diez metros y "
            "un pretil gastado por dos siglos de codos apoyados.\n\n"
            "El agua abajo va negra y sin ruido. Un puente sobre un río que no "
            "suena es una cosa que no debería existir."
        ),
    },
    "boca_alcantarilla": {
        "nombre": "Boca de tormenta de la avenida",
        "exterior": True,
        "desc": (
            "Una tapa de hierro fundido corrida a un costado en el medio de la "
            "calzada, con el escudo de la ciudad en relieve y la fecha de "
            "fundición.\n\n"
            "Del hueco sube aire tibio y olor a agua estancada. Y algo más, "
            "más abajo, que no es olor."
        ),
    },
})

# ==========================================================================
# EL HOSPITAL POR DENTRO
# Plano propio, con sus pisos.
# ==========================================================================

SALAS.update({
    "hos_recepcion": {
        "nombre": "Hospital — hall de admisión",
        "exterior": False,
        "desc": (
            "Piso de linóleo verde agua, sillas de plástico atornilladas en "
            "filas y un mostrador de admisión con un vidrio corredizo.\n\n"
            "El cartel luminoso de turnos marca el número |w47|n. En la sala "
            "hay cuarenta y siete sillas, y todas están vacías."
        ),
    },
    "hos_guardia": {
        "nombre": "Hospital — guardia",
        "exterior": False,
        "desc": (
            "Cuatro boxes separados por cortinas de plástico, cada uno con su "
            "camilla, su monitor y su carro de paro. Tres cortinas están "
            "descorridas.\n\n"
            "La cuarta no. Detrás se oye un monitor marcando un ritmo."
        ),
    },
    "hos_farmacia": {
        "nombre": "Hospital — farmacia",
        "exterior": False,
        "desc": (
            "Estanterías metálicas con la medicación ordenada por principio "
            "activo, y una heladera de vacunas que zumba.\n\n"
            "El armario de psicotrópicos está abierto y vacío. La cerradura no "
            "está forzada: alguien tenía la llave."
        ),
    },
    "hos_quirofano": {
        "nombre": "Hospital — quirófano 2",
        "exterior": False,
        "desc": (
            "Azulejo blanco hasta el techo, una mesa de operaciones bajo la "
            "lámpara cialítica y el instrumental dispuesto sobre un paño "
            "verde, en orden, sin usar.\n\n"
            "La lámpara está encendida y apunta a la mesa. En la mesa no hay "
            "nadie, pero el paño tiene la forma de alguien."
        ),
    },
    "hos_escalera": {
        "nombre": "Hospital — caja de escalera",
        "exterior": False,
        "desc": (
            "Hormigón sin revestir, pasamanos de caño pintado de verde y una "
            "lámpara enjaulada en cada descanso. Los números de piso están "
            "pintados con plantilla.\n\n"
            "El aire se enfría un grado por tramo bajando."
        ),
    },
    "hos_internacion_1": {
        "nombre": "Hospital — internación, primer piso",
        "exterior": False,
        "desc": (
            "Un pasillo largo con puertas numeradas a los dos lados y una "
            "línea verde pintada en el piso. La mitad de las camas están "
            "hechas con sábanas limpias.\n\n"
            "La otra mitad no, y las sábanas están del lado de adentro de las "
            "puertas."
        ),
    },
    "hos_internacion_2": {
        "nombre": "Hospital — internación, segundo piso",
        "exterior": False,
        "desc": (
            "Idéntico al primer piso, hasta en la posición de los carros de "
            "curaciones. Exactamente idéntico.\n\n"
            "La línea del piso, acá, es roja."
        ),
    },
    "hos_morgue": {
        "nombre": "Hospital — morgue",
        "exterior": False,
        "desc": (
            "Subsuelo. Doce cámaras de acero en una pared, tres filas de "
            "cuatro, con sus manijas cromadas y sus fichas en el portafichas.\n\n"
            "Once están cerradas. La doce está abierta y la bandeja afuera, "
            "limpia, con la ficha todavía puesta."
        ),
    },
    "hos_generador": {
        "nombre": "Hospital — sala de máquinas",
        "exterior": False,
        "desc": (
            "Un generador diésel del tamaño de un camión, tableros eléctricos "
            "con las puertas abiertas y un piso de rejilla sobre un canal de "
            "desagüe.\n\n"
            "El tanque de combustible está lleno. Alguien lo llenó hace poco."
        ),
    },
    "hos_helipuerto": {
        "nombre": "Hospital — helipuerto",
        "exterior": True,
        "desc": (
            "Una plataforma circular en la azotea, con la H pintada en blanco "
            "y las luces de balizamiento encendidas alrededor.\n\n"
            "Desde acá se ve toda Nébrida, o se vería: la niebla llega hasta "
            "la altura del parapeto y sigue subiendo."
        ),
    },
})

# ==========================================================================
# LAS ALCANTARILLAS
# ==========================================================================

SALAS.update({
    "alc_pozo": {
        "nombre": "Alcantarillas — pozo de acceso",
        "exterior": False,
        "desc": (
            "Un pozo de hormigón de cuatro metros con escalones de hierro "
            "empotrados. Abajo, una plataforma seca junto a un canal de agua "
            "oscura que corre despacio.\n\n"
            "El eco devuelve tus pasos con medio segundo de retraso. Medio "
            "segundo es demasiado para este tamaño de sala."
        ),
    },
    "alc_colector": {
        "nombre": "Alcantarillas — colector principal",
        "exterior": False,
        "desc": (
            "El caño grande: cuatro metros de diámetro, con una banquina de "
            "cemento a cada lado del canal y una lámpara enjaulada cada veinte "
            "metros.\n\n"
            "La mitad de las lámparas están rotas, y las que funcionan están "
            "todas del mismo lado."
        ),
    },
    "alc_camara": {
        "nombre": "Alcantarillas — cámara de rejas",
        "exterior": False,
        "desc": (
            "Una cámara circular donde desembocan cuatro galerías, con una "
            "isla de hormigón en el medio y rejas de barrotes en tres de las "
            "bocas.\n\n"
            "Contra las rejas se acumuló lo que baja: plástico, ramas, ropa. "
            "Bastante ropa."
        ),
    },
    "alc_oficina": {
        "nombre": "Alcantarillas — oficina de mantenimiento",
        "exterior": False,
        "desc": (
            "Un cuartito de servicio con puerta de chapa: escritorio, silla "
            "giratoria rota, un tablero de llaves y un plano de las galerías "
            "clavado a la pared.\n\n"
            "El plano tiene anotaciones a lápiz que no figuran en ningún plano "
            "oficial."
        ),
    },
})

# --------------------------------------------------------------------------
# CONEXIONES
#
# Solo lo que no es grilla. Las salidas norte/sur/este/oeste entre celdas
# vecinas las crea el constructor: declararlas acá sería duplicar trabajo y
# abrir la puerta a que los datos se contradigan con el dibujo.
#
# Cada tupla es (origen, salida_ida, destino, salida_vuelta). Si el nombre está
# en DIRECCIONES hereda sus alias; si no, los alias se separan con "|".
# --------------------------------------------------------------------------

CONEXIONES = [
    # --- entrar al hospital ---
    ("hospital_frente", "dentro", "hos_recepcion", "fuera"),
    ("hos_recepcion", "este", "hos_guardia", "oeste"),
    ("hos_recepcion", "oeste", "hos_farmacia", "este"),
    ("hos_guardia", "norte", "hos_quirofano", "sur"),
    ("hos_recepcion", "escalera|escaleras", "hos_escalera", "fuera"),
    ("hos_escalera", "arriba", "hos_internacion_1", "abajo"),
    ("hos_internacion_1", "arriba", "hos_internacion_2", "abajo"),
    ("hos_internacion_2", "arriba", "hos_helipuerto", "abajo"),
    ("hos_escalera", "abajo", "hos_morgue", "arriba"),
    ("hos_morgue", "oeste", "hos_generador", "este"),
    # --- bajar a las cloacas ---
    ("boca_alcantarilla", "abajo", "alc_pozo", "arriba"),
    ("alc_pozo", "sur", "alc_colector", "norte"),
    ("alc_colector", "sur", "alc_camara", "norte"),
    ("alc_camara", "oeste", "alc_oficina", "este"),
]
