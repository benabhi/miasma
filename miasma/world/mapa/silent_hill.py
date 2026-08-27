# -*- coding: utf-8 -*-
"""
Datos del mapa de pruebas: la ciudad de Silent Hill (juego de 1999).

Este módulo es **solo datos**. La lógica de construcción vive en
`world.mapa.constructor`. Para agregar una sala alcanza con sumar una entrada a
`SALAS` y las tuplas correspondientes a `CONEXIONES`.

Sobre la fidelidad: la traza está reconstruida a partir de los mapas in-game y
de las guías de silenthillmemories.net. Los nombres de calles, comercios y
salas interiores son los del juego. La topología es una simplificación
navegable: las calles se representan por sus cruces, no metro a metro. Es un
escenario de pruebas, no una maqueta a escala.

Distritos:
    old      Old Silent Hill        cruces de Finney/Matheson/Ellroy/Bloch
                                    con Bradbury/Midwich/Levin/Bachman
    escuela  Midwich Elementary School
    central  Central Silent Hill    Crichton/Koontz/Munson/Katz
                                    con Simmons/Sagan/Bachman
    hospital Alchemilla Hospital
    cloacas  las alcantarillas que unen Central con el área turística
    resort   Silent Hill Resort Area
    parque   Lakeside Amusement Park
"""

# --------------------------------------------------------------------------
# Direcciones y sus alias. La clave es el nombre de la salida; los alias son
# lo que además acepta el parser.
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

# Dirección inversa, para generar la salida de vuelta automáticamente.
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

# Sala donde empieza el juego y a donde vuelven los personajes sin casa.
SALA_INICIO = "int_cafe_5to2"

# Niebla: la constante estética del pueblo. Se antepone a las descripciones de
# exteriores para no repetirla a mano en cada sala.
NIEBLA = (
    "|xLa niebla lo come todo a diez metros. Cae ceniza, mansa, como nieve "
    "sucia.|n\n\n"
)


# --------------------------------------------------------------------------
# SALAS
#
#   nombre     lo que ve el jugador
#   distrito   agrupa y etiqueta (se usa para reconstrucciones parciales)
#   exterior   True antepone NIEBLA a la descripción
#   desc       descripción larga
# --------------------------------------------------------------------------

SALAS = {}

# ==========================================================================
# OLD SILENT HILL
# Grilla de cruces. Calles este-oeste, de norte a sur: Finney, Matheson,
# Ellroy, Bloch. Calles norte-sur, de oeste a este: Bradbury, Midwich, Levin
# y Bachman Road, la arteria que cruza todo el pueblo.
# ==========================================================================

SALAS.update({
    "osh_bachman_norte": {
        "nombre": "Bachman Road — el puente roto",
        "distrito": "old", "exterior": True,
        "desc": (
            "Bachman Road se termina acá, y no por decisión de nadie. El asfalto "
            "se parte en un borde limpio y del otro lado no hay nada: una "
            "garganta de piedra por la que sube aire frío. El puente que cruzaba "
            "hacia el norte está en el fondo, hecho pedazos.\n\n"
            "Un |wpatrullero|n quedó atravesado a centímetros del vacío, con la "
            "puerta del conductor abierta y las balizas todavía girando. No "
            "iluminan nada. La niebla se las traga."
        ),
    },
    "osh_finney_bachman": {
        "nombre": "Finney St. y Bachman Rd.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El cruce más transitado del barrio viejo, en otra vida. Un semáforo "
            "cuelga muerto sobre el medio de la calle y se mece sin viento.\n\n"
            "En la esquina noreste está la |wtienda de conveniencia|n, con los "
            "fluorescentes todavía prendidos y la puerta trabada por un carrito. "
            "Sobre la vereda oeste, la vidriera rota del |wCafé 5to2|n."
        ),
    },
    "osh_finney_levin": {
        "nombre": "Finney St. y Levin St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Casas bajas de tablas pintadas, todas iguales, todas con las "
            "cortinas corridas. Una regadera automática sigue girando sobre un "
            "cantero de pasto quemado.\n\n"
            "Entre dos casas se abre un |wportón ancho|n hacia el oeste, del que "
            "sale olor a goma vieja."
        ),
    },
    "osh_finney_midwich": {
        "nombre": "Finney St. y Midwich St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Un cartel escolar amarillo, de esos con dos siluetas de chicos "
            "tomados de la mano, marca el principio de Midwich Street hacia el "
            "sur. Alguien lo dobló hasta que las siluetas quedaron mirando al "
            "piso.\n\n"
            "Hay bicicletas encadenadas a un poste, oxidadas hasta el cuadro."
        ),
    },
    "osh_finney_bradbury": {
        "nombre": "Finney St. y Bradbury St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El extremo oeste de Finney. La calle sigue veinte metros más y "
            "después no sigue: el pavimento se levantó en placas, como si algo "
            "hubiera empujado desde abajo, y entre las placas hay una oscuridad "
            "sin fondo visible.\n\n"
            "No se pasa. Bradbury Street baja hacia el sur, intacta."
        ),
    },
    "osh_matheson_bachman": {
        "nombre": "Matheson St. y Bachman Rd.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Bachman Road se ensancha para dejar lugar a una parada de colectivo "
            "con techo de chapa. En el banco hay una campera doblada con cuidado, "
            "como si alguien pensara volver a buscarla.\n\n"
            "En la vereda este brilla el cartel de |wQueen Burger|n: la corona de "
            "neón todavía funciona, y parpadea."
        ),
    },
    "osh_matheson_levin": {
        "nombre": "Matheson St. y Levin St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Barrio residencial cerrado sobre sí mismo. Una |wcasilla de perro|n de "
            "madera, volcada de costado, ocupa media vereda; la cadena sigue atada "
            "a la estaca y termina en un collar vacío.\n\n"
            "La casa a la que pertenece tiene la puerta del frente entornada."
        ),
    },
    "osh_matheson_midwich": {
        "nombre": "Matheson St. y Midwich St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Midwich Street sigue bajando hacia el sur, hacia la escuela. Desde "
            "acá ya se ve la silueta del edificio, o algo del tamaño de un "
            "edificio, recortado contra el gris.\n\n"
            "Un |wcolectivo escolar|n amarillo está estacionado mal, montado sobre "
            "el cordón, con la puerta plegable abierta."
        ),
    },
    "osh_matheson_bradbury": {
        "nombre": "Matheson St. y Bradbury St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Bradbury Street tiene, en el medio del asfalto, un |wagujero|n del "
            "ancho de un auto. Los bordes son irregulares y hacia abajo se ve "
            "estructura de hormigón, caños, y después nada.\n\n"
            "Hacia el norte, entre dos medianeras, se abre un callejón angosto."
        ),
    },
})

SALAS.update({
    "osh_ellroy_bachman": {
        "nombre": "Ellroy St. y Bachman Rd.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Una |westación de servicio|n ocupa toda la esquina sureste: cuatro "
            "surtidores bajo una marquesina, el precio del combustible congelado "
            "en un número que ya no significa nada.\n\n"
            "El piso de cemento tiene manchas oscuras que no son aceite."
        ),
    },
    "osh_ellroy_levin": {
        "nombre": "Ellroy St. y Levin St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "Acá las casas dan paso a galpones bajos y depósitos. Un contenedor de "
            "basura volcado desparramó su contenido sobre la calle y nadie lo "
            "juntó.\n\n"
            "Se escucha, muy lejos, algo metálico que golpea a intervalos "
            "regulares."
        ),
    },
    "osh_ellroy_midwich": {
        "nombre": "Ellroy St. y Midwich St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El paredón perimetral de la |wEscuela Primaria Midwich|n corre a lo "
            "largo de toda la vereda sur: ladrillo, tres metros, rematado con una "
            "reja de puntas.\n\n"
            "El portón principal da al sur, entreabierto lo justo para que pase "
            "una persona."
        ),
    },
    "osh_ellroy_bradbury": {
        "nombre": "Ellroy St. y Bradbury St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El sur de Ellroy. La calzada se hunde en una pendiente suave y en el "
            "punto más bajo se juntó agua negra, quieta, cubierta por una película "
            "iridiscente.\n\n"
            "Hacia el oeste hay un callejón sin salida con las escaleras "
            "derrumbadas."
        ),
    },
    "osh_bloch_bachman": {
        "nombre": "Bloch St. y Bachman Rd.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El extremo sur del barrio viejo. Bachman Road dobla hacia el este y "
            "se convierte en la subida al |wpuente levadizo|n, la única forma de "
            "cruzar al centro.\n\n"
            "Un cartel de chapa oxidada anuncia: |xCENTRAL SILENT HILL — 1 MI.|n"
        ),
    },
    "osh_bloch_levin": {
        "nombre": "Bloch St. y Levin St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "La |wIglesia Balkan|n ocupa la esquina sur: piedra gris, un campanario "
            "corto y sin campana, y un vitral que desde afuera se ve negro.\n\n"
            "Las puertas dobles de madera están cerradas, pero no trabadas."
        ),
    },
    "osh_bloch_midwich": {
        "nombre": "Bloch St. y Midwich St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "La parte de atrás de la escuela. El paredón sigue, más bajo, y por "
            "encima asoman los aros oxidados de una cancha interna.\n\n"
            "Sobre la vereda norte hay un local con la persiana a medio bajar."
        ),
    },
    "osh_bloch_bradbury": {
        "nombre": "Bloch St. y Bradbury St.",
        "distrito": "old", "exterior": True,
        "desc": (
            "El oeste de Bloch Street. En la vidriera de |wCut-Rite Chain Saws|n hay "
            "una motosierra sobre un pedestal de terciopelo rojo, iluminada por un "
            "spot que sigue funcionando.\n\n"
            "Más allá, la calle desaparece bajo un derrumbe de mampostería."
        ),
    },
    "osh_callejon_basket": {
        "nombre": "Cancha de básquet",
        "distrito": "old", "exterior": True,
        "desc": (
            "Un rectángulo de cemento entre medianeras, con dos tableros de madera "
            "terciada y una red que son tres hilos colgando. Alguien pintó las "
            "líneas a mano, y las pintó torcidas.\n\n"
            "Hay una pelota en un rincón, desinflada, con la marca de un pie "
            "encima."
        ),
    },
    "osh_callejon_gordon": {
        "nombre": "Callejón detrás de Bradbury",
        "distrito": "old", "exterior": True,
        "desc": (
            "Un pasillo de servicio de dos metros de ancho entre los fondos de dos "
            "casas. Cables de ropa cruzan de una medianera a la otra, cargados de "
            "prendas empapadas que gotean ceniza.\n\n"
            "Al fondo, una puerta trasera con el apellido |wGORDON|n grabado en una "
            "chapita de bronce."
        ),
    },
    "osh_puente_levadizo": {
        "nombre": "El puente levadizo",
        "distrito": "old", "exterior": True,
        "desc": (
            "Dos hojas de acero remachado que se levantan desde el medio para "
            "dejar pasar embarcaciones que hace décadas no pasan. Ahora están "
            "abajo, y el tablero cruza sobre agua negra hacia el centro del "
            "pueblo.\n\n"
            "A un costado se levanta la |wtorre de control|n, una caja de vidrio "
            "sobre cuatro patas de hierro."
        ),
    },
    "osh_torre_control": {
        "nombre": "Torre de control del puente",
        "distrito": "old", "exterior": False,
        "desc": (
            "Una cabina de vidrio a seis metros del suelo, con vista a los dos "
            "lados del canal. Adentro hay un tablero con dos palancas grandes de "
            "goma roja, un manual plastificado y un termo.\n\n"
            "El termo todavía está tibio."
        ),
    },
})

# --- Interiores de Old Silent Hill ---------------------------------------

SALAS.update({
    "int_cafe_5to2": {
        "nombre": "Café 5to2",
        "distrito": "old", "exterior": False,
        "desc": (
            "Un bar de esquina de doce mesas, con piso de damero y bancos de "
            "cuerina roja rajada. La vidriera que da a Finney está reventada hacia "
            "adentro y el vidrio cruje bajo cualquier paso.\n\n"
            "Sobre el mostrador, junto a una taza con café frío y una raya de "
            "carmín en el borde, hay una |wradio portátil|n encendida. No transmite "
            "nada: solo estática, que a veces sube de golpe y después baja.\n\n"
            "El reloj de pared marca las |w5 menos 2|n. No se mueve."
        ),
    },
    "int_tienda": {
        "nombre": "Tienda de conveniencia",
        "distrito": "old", "exterior": False,
        "desc": (
            "Cuatro góndolas paralelas bajo tubos fluorescentes que zumban. Las "
            "heladeras del fondo siguen funcionando y adentro todo está en "
            "perfecto estado, prolijo, alineado con la etiqueta hacia afuera.\n\n"
            "En la caja registradora, el cajón está abierto y lleno."
        ),
    },
    "int_queen_burger": {
        "nombre": "Queen Burger",
        "distrito": "old", "exterior": False,
        "desc": (
            "Plástico naranja, mesas atornilladas al piso y un mural de una "
            "hamburguesa con corona. Las freidoras están frías pero el aceite "
            "sigue adentro, coagulado.\n\n"
            "Todas las bandejas de las mesas están servidas y sin tocar."
        ),
    },
    "int_casa_levin": {
        "nombre": "Casa de Levin Street",
        "distrito": "old", "exterior": False,
        "desc": (
            "Un living de casa de familia con la tele prendida en un canal sin "
            "señal. Hay juguetes ordenados en una caja, fotos en la repisa, y un "
            "olor dulce y pesado que viene de la cocina.\n\n"
            "La puerta trasera tiene tres cerraduras distintas, todas puestas del "
            "lado de adentro."
        ),
    },
    "int_casa_gordon": {
        "nombre": "Casa de K. Gordon",
        "distrito": "old", "exterior": False,
        "desc": (
            "Una cocina angosta que da a un pasillo con papel de pared "
            "despegándose en tiras. Sobre la mesa hay un diario abierto y "
            "subrayado con birome, y una escopeta desarmada sobre un trapo.\n\n"
            "Faltan piezas."
        ),
    },
    "int_iglesia_balkan": {
        "nombre": "Iglesia Balkan",
        "distrito": "old", "exterior": False,
        "desc": (
            "Una nave de veinte bancos con el techo más alto de lo que el "
            "edificio prometía desde afuera. El vitral, visto desde adentro, es "
            "una figura circular de rayos y espadas que no corresponde a ninguna "
            "iconografía conocida.\n\n"
            "Sobre el altar hay velas encendidas. Alguien las repone."
        ),
    },
    "int_cut_rite": {
        "nombre": "Cut-Rite Chain Saws",
        "distrito": "old", "exterior": False,
        "desc": (
            "Un local largo y angosto con motosierras colgadas de ganchos en las "
            "dos paredes, de la más chica a la más grande. Olor a nafta, aceite de "
            "cadena y aserrín.\n\n"
            "El mostrador tiene una amoladora y un banco de trabajo con las "
            "herramientas ordenadas por tamaño."
        ),
    },
    "int_estacion_servicio": {
        "nombre": "Estación de servicio — taller",
        "distrito": "old", "exterior": False,
        "desc": (
            "El box de reparaciones, con la fosa abierta en el piso y un elevador "
            "hidráulico a media altura sosteniendo nada. Estanterías de repuestos, "
            "un compresor, bidones apilados contra la pared.\n\n"
            "En la fosa hay una linterna encendida, apuntando hacia arriba."
        ),
    },
})

# ==========================================================================
# MIDWICH ELEMENTARY SCHOOL
# Planta baja alrededor de un patio con torre de reloj; primer piso con el
# laboratorio de química, la sala de música y la biblioteca; sótano con la
# caldera.
# ==========================================================================

SALAS.update({
    "esc_entrada": {
        "nombre": "Escuela Midwich — patio de entrada",
        "distrito": "escuela", "exterior": True,
        "desc": (
            "Un patio de cemento entre el portón y la puerta principal, con un "
            "mástil sin bandera y dos canteros de tierra seca. Sobre el dintel, "
            "letras de bronce: |wMIDWICH ELEMENTARY SCHOOL|n.\n\n"
            "El |wcolectivo escolar|n está estacionado contra el paredón, con el "
            "motor todavía tibio y las llaves puestas."
        ),
    },
    "esc_recepcion": {
        "nombre": "Escuela Midwich — hall de recepción",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Un hall con piso encerado que devuelve el reflejo de los tubos. "
            "Vitrina de trofeos, un mostrador de conserjería y un |wplano de la "
            "escuela|n atornillado a la pared.\n\n"
            "Detrás del mostrador hay un cuadro torcido y, debajo, una mancha en "
            "la pared con la forma exacta de otro cuadro."
        ),
    },
    "esc_enfermeria": {
        "nombre": "Escuela Midwich — enfermería",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Dos camillas con sábanas de papel, un biombo, un botiquín de metal "
            "blanco y una balanza de pie con la aguja trabada en un número "
            "imposible para un chico.\n\n"
            "Huele a alcohol y, debajo, a algo más viejo."
        ),
    },
    "esc_patio": {
        "nombre": "Escuela Midwich — patio interno",
        "distrito": "escuela", "exterior": True,
        "desc": (
            "Un patio rectangular rodeado por los cuatro pasillos de la escuela. "
            "El piso está pintado con una rayuela y un círculo para juegos.\n\n"
            "En el centro se levanta la |wtorre del reloj|n: ladrillo, seis metros, "
            "con una esfera de números romanos en cada cara. Las cuatro esferas "
            "marcan horas distintas."
        ),
    },
    "esc_torre_reloj": {
        "nombre": "Escuela Midwich — base de la torre del reloj",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Un cubículo de ladrillo del tamaño de un placard, al pie de la torre. "
            "Adentro hay una escalera de hierro que sube hacia el mecanismo y un "
            "eje vertical con tres ruedas dentadas.\n\n"
            "Falta una manivela. El hueco donde iba está limpio y engrasado."
        ),
    },
    "esc_pasillo_pb_izq": {
        "nombre": "Escuela Midwich — pasillo oeste (PB)",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Percheros a la altura de un chico de ocho años, todos ocupados. "
            "Camperas, mochilas, un par de botas de lluvia amarillas.\n\n"
            "Al fondo, la escalera al primer piso y las puertas de los baños."
        ),
    },
    "esc_pasillo_pb_der": {
        "nombre": "Escuela Midwich — pasillo este (PB)",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Dibujos pegados con cinta a lo largo de toda la pared, hechos con "
            "crayón grueso. Casas, soles, familias. Todos tienen, en algún lugar "
            "del papel, la misma figura circular de rayos y espadas.\n\n"
            "Puertas dobles al patio y una escalera al fondo."
        ),
    },
    "esc_aula_pb": {
        "nombre": "Escuela Midwich — aula 1-A",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Veinticuatro pupitres de madera en cuatro filas, todos con la silla "
            "levantada sobre la mesa como al final del día. En el pizarrón hay una "
            "lista de nombres escrita con letra prolija de maestra.\n\n"
            "Uno de los nombres está tachado con tanta fuerza que rompió el "
            "pizarrón."
        ),
    },
    "esc_pasillo_1p_izq": {
        "nombre": "Escuela Midwich — pasillo oeste (1er piso)",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Más angosto que el de abajo, y más oscuro: la mitad de los tubos no "
            "prenden. Hay una puerta con un cartel de |wAZOTEA — PROHIBIDO EL "
            "PASO|n, cerrada con candado.\n\n"
            "El aire acá está varios grados más frío."
        ),
    },
    "esc_lab_quimica": {
        "nombre": "Escuela Midwich — laboratorio de química",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Mesadas de piedra negra con mecheros, piletas y grifos de gas. Una "
            "vitrina con frascos etiquetados a mano, ordenados alfabéticamente.\n\n"
            "Sobre la mesada del fondo hay una balanza de platillos con una "
            "|wmedalla dorada|n en uno de los lados. El otro platillo está vacío y, "
            "sin embargo, la balanza está equilibrada."
        ),
    },
    "esc_sala_musica": {
        "nombre": "Escuela Midwich — sala de música",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Gradas de madera para el coro y, contra la pared, un |wpiano vertical|n "
            "con la tapa abierta. Cinco teclas están decoloradas, como si las "
            "hubieran tocado mil veces más que al resto.\n\n"
            "Sobre el atril, una partitura escrita a mano que no tiene notas: "
            "tiene dibujos de pájaros."
        ),
    },
    "esc_biblioteca": {
        "nombre": "Escuela Midwich — biblioteca",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Ocho estanterías bajas y cuatro mesas de lectura. El fichero de "
            "cartón está abierto en la letra M y falta una ficha.\n\n"
            "Todos los libros están dados vuelta, con el lomo hacia adentro."
        ),
    },
    "esc_reserva": {
        "nombre": "Escuela Midwich — depósito de la biblioteca",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "Un cuarto sin ventanas, del ancho de dos estanterías, con cajas de "
            "material viejo apiladas hasta el techo. Huele a papel húmedo.\n\n"
            "En el piso, entre dos cajas, hay una silla de chico dada vuelta."
        ),
    },
    "esc_caldera": {
        "nombre": "Escuela Midwich — sala de calderas",
        "distrito": "escuela", "exterior": False,
        "desc": (
            "El sótano: caños forrados, un piso de rejilla y una caldera de hierro "
            "del tamaño de un auto, apagada. El manómetro marca presión.\n\n"
            "Detrás de la caldera, la pared de ladrillo tiene un hueco del que "
            "sale aire caliente y olor a óxido."
        ),
    },
    "esc_azotea": {
        "nombre": "Escuela Midwich — azotea",
        "distrito": "escuela", "exterior": True,
        "desc": (
            "Una superficie plana de membrana asfáltica, con la maquinaria de "
            "ventilación y el tanque de agua. Desde el parapeto se ve la niebla "
            "cerrada en todas las direcciones.\n\n"
            "La torre del reloj asoma desde el patio, y desde acá se ve que la "
            "esfera que da al norte no tiene agujas."
        ),
    },
})

# ==========================================================================
# CENTRAL SILENT HILL
# Calles este-oeste, de norte a sur: Crichton, Koontz, Munson, Katz.
# Calles norte-sur, de oeste a este: Simmons, Sagan, Bachman Road.
# ==========================================================================

SALAS.update({
    "csh_cabecera_puente": {
        "nombre": "Cabecera este del puente",
        "distrito": "central", "exterior": True,
        "desc": (
            "La bajada del puente levadizo del lado del centro. Acá el pueblo "
            "cambia: las casas de madera dejan lugar a edificios de tres y cuatro "
            "pisos, con locales a la calle y persianas metálicas.\n\n"
            "Una garita de peaje vacía, con la barrera levantada."
        ),
    },
    "csh_crichton_bachman": {
        "nombre": "Crichton St. y Bachman Rd.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El extremo noreste del centro. En la esquina, con vidriera enrejada y "
            "un toldo verde descolorido, está |wAntigüedades Green Lion|n. El cartel "
            "tiene un león rampante pintado a mano.\n\n"
            "Bachman Road sigue hacia el sur, hacia el área turística."
        ),
    },
    "csh_crichton_sagan": {
        "nombre": "Crichton St. y Sagan St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El frente de la |wComisaría de Silent Hill|n ocupa la vereda sur: un "
            "edificio bajo de ladrillo visto, con dos escalones de granito y un "
            "farol azul sobre la puerta.\n\n"
            "El farol está prendido. Es la única luz honesta en varias cuadras."
        ),
    },
    "csh_crichton_simmons": {
        "nombre": "Crichton St. y Simmons St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El noroeste del centro. Simmons Street se abre hacia el sur, ancha, "
            "con cantero central y árboles pelados en fila.\n\n"
            "Un semáforo peatonal repite su chicharra de cruce seguro para nadie."
        ),
    },
    "csh_koontz_bachman": {
        "nombre": "Koontz St. y Bachman Rd.",
        "distrito": "central", "exterior": True,
        "desc": (
            "Edificios de departamentos con balcones franceses y macetas muertas. "
            "En la planta baja, una lavandería automática con las máquinas "
            "girando.\n\n"
            "Todas las máquinas están vacías."
        ),
    },
    "csh_koontz_sagan": {
        "nombre": "Koontz St. y Sagan St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "Sobre la vereda sur, detrás de una reja de lanzas y un cantero de boj "
            "sin podar, está el patio de entrada del |wHospital Alchemilla|n.\n\n"
            "La rampa de ambulancias está vacía. El cartel de |xGUARDIA|n sigue "
            "encendido en rojo."
        ),
    },
    "csh_koontz_simmons": {
        "nombre": "Koontz St. y Simmons St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "En la esquina noroeste, el |wCafé Sun|n: mesas de chapa sobre la "
            "vereda, sombrillas plegadas y atadas, una pizarra con el menú del día "
            "borrado a medias.\n\n"
            "Hacia el sur, sobre Simmons, se levanta la mole del centro comercial."
        ),
    },
})

SALAS.update({
    "csh_munson_bachman": {
        "nombre": "Munson St. y Bachman Rd.",
        "distrito": "central", "exterior": True,
        "desc": (
            "Una cuadra de oficinas y estudios contables, con placas de bronce "
            "junto a cada puerta. Ninguna ventana está iluminada.\n\n"
            "Un auto quedó cruzado en el medio del cruce, con las cuatro puertas "
            "abiertas y sin una sola marca de golpe."
        ),
    },
    "csh_munson_sagan": {
        "nombre": "Munson St. y Sagan St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El corazón administrativo del pueblo: municipalidad, correo, un banco "
            "con las cortinas metálicas bajas.\n\n"
            "Sobre el buzón del correo alguien apoyó una pila de cartas prolija, "
            "atada con hilo. Están todas dirigidas a la misma casa."
        ),
    },
    "csh_munson_simmons": {
        "nombre": "Munson St. y Simmons St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El acceso principal del |wSilent Hill Town Center|n, con puertas "
            "giratorias de vidrio y un directorio iluminado por dentro.\n\n"
            "Adentro se ve el reflejo de escaleras mecánicas en movimiento."
        ),
    },
    "csh_katz_bachman": {
        "nombre": "Katz St. y Bachman Rd.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El límite sur del centro. Bachman Road se angosta y empieza a bajar "
            "hacia el lago; de acá en adelante hay pinos a los dos lados.\n\n"
            "Un cartel verde de ruta: |xRESORT AREA / TOLUCA LAKE — 2 MI.|n"
        ),
    },
    "csh_katz_sagan": {
        "nombre": "Katz St. y Sagan St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "Una calle de depósitos y muelles de carga, con las cortinas de chapa "
            "cerradas y candadas.\n\n"
            "En el medio de la calzada, una |wtapa de alcantarilla|n corrida a un "
            "costado. Del hueco sube aire tibio y olor a agua estancada."
        ),
    },
    "csh_katz_simmons": {
        "nombre": "Katz St. y Simmons St.",
        "distrito": "central", "exterior": True,
        "desc": (
            "El sudoeste del centro, contra el paredón trasero del centro "
            "comercial. Contenedores de residuos, cajas de cartón deshechas por la "
            "humedad, un montacargas volcado.\n\n"
            "La calle sigue hacia el oeste, pero a media cuadra la corta un "
            "derrumbe."
        ),
    },
})

# --- Interiores de Central Silent Hill ------------------------------------

SALAS.update({
    "int_comisaria": {
        "nombre": "Comisaría de Silent Hill",
        "distrito": "central", "exterior": False,
        "desc": (
            "Un mostrador de atención al público con vidrio blindado y un "
            "pasapapeles de acero. Detrás, escritorios con computadoras encendidas "
            "y expedientes abiertos.\n\n"
            "En el corcho de la pared hay veinte fotos de personas desaparecidas. "
            "Diecinueve están tachadas con una cruz roja."
        ),
    },
    "int_green_lion": {
        "nombre": "Antigüedades Green Lion",
        "distrito": "central", "exterior": False,
        "desc": (
            "Un local abarrotado hasta el techo: relojes de pie, espejos con marco "
            "de yeso, cajones de porcelana, muñecas de porcelana. Todo tiene una "
            "etiqueta de precio escrita a mano.\n\n"
            "Los relojes están todos parados, y todos en la misma hora."
        ),
    },
    "int_cafe_sun": {
        "nombre": "Café Sun",
        "distrito": "central", "exterior": False,
        "desc": (
            "Una cafetería luminosa de ocho mesas, con azulejos amarillos y una "
            "máquina de espresso italiana sobre el mostrador. La máquina está "
            "encendida y mantiene la presión.\n\n"
            "Hay un diario del día doblado sobre una mesa. La fecha no coincide "
            "con ninguna que hayas visto."
        ),
    },
    "int_town_center": {
        "nombre": "Silent Hill Town Center — atrio",
        "distrito": "central", "exterior": False,
        "desc": (
            "Un atrio de tres niveles bajo una claraboya que no deja pasar luz. "
            "Las escaleras mecánicas suben y bajan sin nadie encima; el ruido de "
            "los engranajes llena todo el volumen del edificio.\n\n"
            "En el centro hay una fuente seca, llena de monedas."
        ),
    },
})

# ==========================================================================
# HOSPITAL ALCHEMILLA
# Planta baja completa; sótano con el generador; pisos 2 y 3 por ascensor.
# ==========================================================================

SALAS.update({
    "hos_patio": {
        "nombre": "Hospital Alchemilla — patio de entrada",
        "distrito": "hospital", "exterior": True,
        "desc": (
            "Un patio delantero con cantero de boj y un banco de cemento, entre la "
            "reja de Koontz Street y las puertas del hospital.\n\n"
            "Una silla de ruedas quedó en el medio del camino, frenada, mirando "
            "hacia la salida."
        ),
    },
    "hos_recepcion": {
        "nombre": "Hospital Alchemilla — hall de recepción",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Piso de linóleo verde agua, sillas de plástico atornilladas en filas y "
            "un mostrador de admisión con un vidrio corredizo.\n\n"
            "El cartel luminoso de turnos marca el número |w47|n. En la sala hay "
            "cuarenta y siete sillas, y todas están vacías."
        ),
    },
    "hos_oficina": {
        "nombre": "Hospital Alchemilla — administración",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Detrás del mostrador: dos escritorios, un fichero de historias "
            "clínicas y un tablero de llaves con ganchos numerados.\n\n"
            "Faltan tres llaves. Los ganchos vacíos son el 3, el 8 y el 23."
        ),
    },
    "hos_examen": {
        "nombre": "Hospital Alchemilla — sala de exámenes",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Una camilla con papel, un negatoscopio encendido y un carro de "
            "instrumental cubierto con un paño verde.\n\n"
            "En el negatoscopio hay una placa de tórax. La caja torácica tiene una "
            "costilla de más, y esa costilla no es hueso."
        ),
    },
    "hos_farmacia": {
        "nombre": "Hospital Alchemilla — farmacia",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Estanterías metálicas con cajas de medicación ordenadas por principio "
            "activo, y una heladera de vacunas que zumba.\n\n"
            "Sobre el mostrador, un recorte de diario pegado con cinta. El titular "
            "habla de una desaparición; la foto está recortada."
        ),
    },
    "hos_consultorio": {
        "nombre": "Hospital Alchemilla — consultorio",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Escritorio de madera, dos sillas, un diploma enmarcado y un "
            "esqueleto anatómico en un rincón.\n\n"
            "Sobre el secante hay un |wplano del subsuelo|n desplegado, con una zona "
            "marcada en birome roja y, al lado, escrito con la misma birome: "
            "|xno bajar solo|n."
        ),
    },
    "hos_reuniones": {
        "nombre": "Hospital Alchemilla — sala de reuniones",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Una mesa ovalada para doce, un proyector y una pizarra con un "
            "organigrama a medio borrar.\n\n"
            "Doce vasos de agua servidos. Once están llenos."
        ),
    },
    "hos_cocina": {
        "nombre": "Hospital Alchemilla — cocina",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Cocina industrial de acero inoxidable, con ollas del tamaño de un "
            "tambor y una cámara frigorífica con la puerta apenas abierta.\n\n"
            "De la cámara sale vapor frío y un zumbido de motor."
        ),
    },
    "hos_direccion": {
        "nombre": "Hospital Alchemilla — dirección",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "La oficina del director: alfombra, biblioteca de roble, un sillón de "
            "cuero y ventanales que dan a la niebla.\n\n"
            "Sobre el escritorio hay un frasco de vidrio roto y un charco de un "
            "líquido ámbar que no se secó. Al lado, un mortero."
        ),
    },
    "hos_ascensor": {
        "nombre": "Hospital Alchemilla — ascensor",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Una cabina de acero cepillado con espejo en el fondo y una botonera "
            "de cinco pisos. La luz de emergencia está encendida.\n\n"
            "El indicador de piso muestra un número que no está en la botonera."
        ),
    },
    "hos_escalera_sotano": {
        "nombre": "Hospital Alchemilla — escalera al subsuelo",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Una escalera de hormigón sin revestir, con pasamanos de caño pintado "
            "y una lámpara enjaulada en cada descanso.\n\n"
            "El aire se enfría un grado por escalón."
        ),
    },
    "hos_generador": {
        "nombre": "Hospital Alchemilla — sala de máquinas",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "El subsuelo: un generador diésel del tamaño de un camión, tableros "
            "eléctricos con las puertas abiertas y un piso de rejilla sobre un "
            "canal de desagüe.\n\n"
            "El tanque de combustible está lleno. Alguien lo llenó hace poco."
        ),
    },
    "hos_pasillo_2": {
        "nombre": "Hospital Alchemilla — internación (2do piso)",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Un pasillo largo con puertas numeradas a los dos lados y una línea "
            "verde pintada en el piso. La mitad de las camas están hechas con "
            "sábanas limpias.\n\n"
            "La otra mitad no están hechas, y las sábanas están del lado de "
            "adentro de las puertas."
        ),
    },
    "hos_pasillo_3": {
        "nombre": "Hospital Alchemilla — internación (3er piso)",
        "distrito": "hospital", "exterior": False,
        "desc": (
            "Idéntico al segundo piso, hasta en la posición de los carros de "
            "curaciones. Exactamente idéntico.\n\n"
            "La línea del piso, acá, es roja."
        ),
    },
})

# ==========================================================================
# LAS ALCANTARILLAS
# Unen Katz St. (centro) con el área turística.
# ==========================================================================

SALAS.update({
    "alc_entrada": {
        "nombre": "Alcantarillas — pozo de acceso",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Un pozo de hormigón de cuatro metros con escalones de hierro "
            "empotrados. Abajo, una plataforma seca junto a un canal de agua "
            "oscura que corre despacio.\n\n"
            "El eco devuelve tus pasos con medio segundo de retraso. Medio segundo "
            "es demasiado para este tamaño de sala."
        ),
    },
    "alc_tunel_norte": {
        "nombre": "Alcantarillas — túnel norte",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Un caño de sección ovalada por el que se puede caminar erguido, con "
            "una banquina de cemento a cada lado del canal. Cada veinte metros, "
            "una lámpara enjaulada.\n\n"
            "La mitad de las lámparas están rotas, y las que funcionan están todas "
            "del mismo lado."
        ),
    },
    "alc_cruce": {
        "nombre": "Alcantarillas — cruce de galerías",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Cuatro bocas de túnel dan a una cámara circular con una isla central "
            "de hormigón. El agua entra por tres y sale por una.\n\n"
            "La galería del este está cerrada con una |wreja|n de barrotes y "
            "candado. La del sur, abierta."
        ),
    },
    "alc_oficina": {
        "nombre": "Alcantarillas — oficina de mantenimiento",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Un cuartito de servicio con una puerta de chapa: escritorio, una silla "
            "giratoria rota, un tablero con llaves y un |wplano de las galerías|n "
            "clavado a la pared.\n\n"
            "El plano tiene anotaciones a lápiz que no figuran en ningún plano "
            "oficial."
        ),
    },
    "alc_nivel_superior": {
        "nombre": "Alcantarillas — pasarela superior",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Una pasarela de rejilla metálica a tres metros del agua, con baranda "
            "de un solo lado. Se llega por una escalera vertical.\n\n"
            "Desde acá se ve todo el recorrido del canal. Se ve, también, que el "
            "agua no corre siempre en la misma dirección."
        ),
    },
    "alc_tunel_sur": {
        "nombre": "Alcantarillas — túnel sur",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "El tramo más largo. Acá el caño se angosta y hay que caminar por el "
            "agua, que llega a media pantorrilla y está tibia.\n\n"
            "Contra la pared, a la altura de la cabeza, hay marcas de cinco dedos "
            "arrastrados. Van en dirección contraria a la salida."
        ),
    },
    "alc_salida": {
        "nombre": "Alcantarillas — boca de salida",
        "distrito": "cloacas", "exterior": False,
        "desc": (
            "Una cámara final con una escalera vertical que sube hacia una tapa de "
            "hierro con luz gris colándose por las ranuras.\n\n"
            "Huele a pinos y a lago."
        ),
    },
})

# ==========================================================================
# SILENT HILL RESORT AREA
# La franja turística sobre la costa norte del lago Toluca.
# ==========================================================================

SALAS.update({
    "res_bachman": {
        "nombre": "Bachman Rd. — entrada al área turística",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Bachman Road termina en una rotonda con un cantero de piedras "
            "pintadas de blanco y un cartel de madera tallada: |wBIENVENIDOS AL "
            "SILENT HILL RESORT|n, con un dibujo de un velero.\n\n"
            "Hacia el sur se escucha agua contra madera."
        ),
    },
    "res_craig": {
        "nombre": "Craig St.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Una calle corta de dos cuadras con locales de temporada: alquiler de "
            "kayaks, una heladería cerrada, una tienda de souvenirs.\n\n"
            "Sobre la vereda oeste, el cartel de neón de |wAnnie's Bar|n zumba y "
            "parpadea en rojo."
        ),
    },
    "res_weaver": {
        "nombre": "Weaver St.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Casas de veraneo de dos plantas con porches de madera y hamacas "
            "colgadas. Todas cerradas con postigos.\n\n"
            "En la esquina está |wIndian Runner|n, una librería de usados con la "
            "puerta cerrada con candado. Más al sur, el playón del motel."
        ),
    },
    "res_nathan": {
        "nombre": "Nathan Ave.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "La avenida ancha del paseo, con palmeras de plástico y una hilera de "
            "carteleras publicitarias iluminadas: |wPete's Bowl-O-Rama|n, |wLakeside "
            "Amusement Park|n, |wHeaven's Night|n, |wLakeview Hotel|n.\n\n"
            "Todas las carteleras funcionan. Es la única calle del pueblo con luz "
            "de verdad."
        ),
    },
    "res_bartlett": {
        "nombre": "Bartlett St.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Una calle arbolada que sube en pendiente suave hasta la explanada del "
            "|wLakeview Hotel|n: seis pisos de ladrillo claro, toldos verdes y una "
            "marquesina con luces de globo.\n\n"
            "La mitad de los globos están fundidos."
        ),
    },
    "res_sandford": {
        "nombre": "Sandford St.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "El extremo oeste del área turística. La calle corre paralela a la "
            "costa, con un paredón bajo de piedra del lado del agua.\n\n"
            "Bajo la letra F del cartel de la calle, la vereda se hundió y dejó a "
            "la vista una escalera derrumbada."
        ),
    },
    "res_puente_sandford": {
        "nombre": "Puente de Sandford St.",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Un puente peatonal de madera y hierro sobre un brazo del lago. Los "
            "tablones están hinchados de humedad y ceden un poco en el medio.\n\n"
            "Del otro lado, la niebla es más espesa. Y hay estática, todo el "
            "tiempo, más fuerte cuanto más avanzás."
        ),
    },
    "res_muelle": {
        "nombre": "Muelle del lago Toluca",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Un muelle de tablones que entra treinta metros en el agua, con "
            "bitas de hierro y neumáticos colgados como defensas.\n\n"
            "Hay una lancha amarrada al final, con el motor fuera de borda "
            "levantado. El agua está negra y absolutamente quieta."
        ),
    },
    "res_faro": {
        "nombre": "El faro",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Una torre blanca y roja de doce metros sobre una punta de piedra. La "
            "puerta de hierro está soldada por el óxido.\n\n"
            "La linterna gira. Cada doce segundos el haz barre la niebla y no "
            "ilumina absolutamente nada."
        ),
    },
    "res_entrada_parque": {
        "nombre": "Entrada del Lakeside Amusement Park",
        "distrito": "resort", "exterior": True,
        "desc": (
            "Un arco de hierro forjado con letras recortadas y guirnaldas de "
            "lamparitas, sobre molinetes de acceso pintados de rojo.\n\n"
            "Los molinetes están destrabados. De adentro sale música de calesita, "
            "a volumen bajo, en loop."
        ),
    },
})

# --- Interiores del área turística ---------------------------------------

SALAS.update({
    "int_annies_bar": {
        "nombre": "Annie's Bar",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Un bar largo con barra de madera lustrada, taburetes altos y dos "
            "|wmesas de pool|n al fondo, bajo lámparas de pantalla verde.\n\n"
            "En una de las mesas la partida quedó a medio jugar. Los tacos están "
            "apoyados contra el borde, no en el atril."
        ),
    },
    "int_indian_runner": {
        "nombre": "Indian Runner",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Una librería de usados con pasillos de un metro entre estanterías que "
            "llegan al techo. Olor a papel viejo y a humedad.\n\n"
            "Sobre el mostrador hay una pila de libros con un cartel escrito a "
            "mano: |xRESERVADOS — NO VENDER|n. Todos son el mismo libro."
        ),
    },
    "int_motel_recepcion": {
        "nombre": "Motel Haerbey Inn — recepción",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Un mostrador con timbre de mesa, un tablero de llaves con doce "
            "casilleros y una máquina de hielo que ronronea en el rincón.\n\n"
            "El libro de huéspedes está abierto. La última entrada es de hoy, y la "
            "firma es un garabato repetido veinte veces."
        ),
    },
    "int_motel_hab3": {
        "nombre": "Motel Haerbey Inn — habitación 3",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Una cama doble con colcha estampada, una mesa de luz, un televisor "
            "atornillado a la cómoda y un cuadro de un lago que no es este lago.\n\n"
            "La cama está deshecha de un solo lado."
        ),
    },
    "int_motel_garage": {
        "nombre": "Motel Haerbey Inn — garage",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Un box de chapa con piso de cemento manchado, un banco de trabajo y "
            "una |wmoto|n sobre el caballete, desarmada a medias.\n\n"
            "Las piezas están alineadas en el piso en el orden exacto en que "
            "salieron."
        ),
    },
    "int_bowl_o_rama": {
        "nombre": "Pete's Bowl-O-Rama",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Ocho pistas de bowling con las máquinas de pinos encendidas y los "
            "monitores de puntaje prendidos en cero. El piso encerado brilla bajo "
            "luces de colores.\n\n"
            "En la pista 4 hay una bola detenida a mitad de camino. No se mueve, "
            "pero tampoco parece haberse frenado."
        ),
    },
    "int_hotel_lakeview": {
        "nombre": "Lakeview Hotel — vestíbulo",
        "distrito": "resort", "exterior": False,
        "desc": (
            "Un lobby de hotel de otra época: alfombra con guardas, sillones de "
            "cuero, una araña de caireles y un mostrador de conserjería de mármol.\n\n"
            "Detrás del mostrador, el casillero de correspondencia tiene un sobre "
            "en cada casilla. Todos los sobres están vacíos."
        ),
    },
})

# ==========================================================================
# LAKESIDE AMUSEMENT PARK
# ==========================================================================

SALAS.update({
    "par_explanada": {
        "nombre": "Parque — explanada central",
        "distrito": "parque", "exterior": True,
        "desc": (
            "Un playón de baldosas con bancos, tachos de basura con forma de "
            "animal y guirnaldas de banderines mojados que cuelgan sin viento.\n\n"
            "Desde acá salen los senderos a las atracciones. La música de calesita "
            "viene del norte, y no se le escucha el corte del loop."
        ),
    },
    "par_heladeria": {
        "nombre": "Parque — heladería",
        "distrito": "parque", "exterior": False,
        "desc": (
            "Un kiosco de madera pintada con un mostrador alto y una vitrina "
            "refrigerada con doce baldes de helado, todos intactos.\n\n"
            "La máquina de barquillos está encendida y la plancha, caliente."
        ),
    },
    "par_vuelta_al_mundo": {
        "nombre": "Parque — la vuelta al mundo",
        "distrito": "parque", "exterior": True,
        "desc": (
            "La rueda gigante ocupa todo el cielo visible: treinta metros de "
            "estructura blanca con cabinas rojas y azules.\n\n"
            "Gira. Despacio, sin apuro, con las puertas de las cabinas abiertas."
        ),
    },
    "par_montana_rusa": {
        "nombre": "Parque — la montaña rusa",
        "distrito": "parque", "exterior": True,
        "desc": (
            "Un entramado de madera y acero que se pierde hacia arriba en la "
            "niebla. La estación de embarque tiene el andén levantado y las "
            "barandas de seguridad bajas.\n\n"
            "El tren no está. Cada tanto se escucha, muy arriba, el traqueteo de "
            "algo que pasa."
        ),
    },
    "par_calesita": {
        "nombre": "Parque — la calesita",
        "distrito": "parque", "exterior": True,
        "desc": (
            "Una plataforma circular bajo una carpa de rayas rojas y blancas, con "
            "veinte caballos de madera empalados en barras de bronce.\n\n"
            "Gira, y la música sale de un organillo mecánico en el centro. Los "
            "caballos suben y bajan. Ninguno está en la misma posición que en la "
            "vuelta anterior."
        ),
    },
})

# --------------------------------------------------------------------------
# CONEXIONES
#
# Cada tupla es (origen, salida_ida, destino, salida_vuelta).
#
#   - Si el nombre de la salida está en DIRECCIONES, hereda sus alias.
#   - Si no, es una salida con nombre propio ("iglesia", "ascensor"). Los
#     alias se separan con "|":  "café|cafe|5to2".
#   - salida_vuelta = None crea una conexión de una sola mano.
# --------------------------------------------------------------------------

CONEXIONES = []

# --- Old Silent Hill: grilla este-oeste -----------------------------------
for _calle in ("finney", "matheson", "ellroy", "bloch"):
    CONEXIONES += [
        (f"osh_{_calle}_bradbury", "este", f"osh_{_calle}_midwich", "oeste"),
        (f"osh_{_calle}_midwich", "este", f"osh_{_calle}_levin", "oeste"),
        (f"osh_{_calle}_levin", "este", f"osh_{_calle}_bachman", "oeste"),
    ]

# --- Old Silent Hill: grilla norte-sur ------------------------------------
for _avenida in ("bradbury", "midwich", "levin", "bachman"):
    CONEXIONES += [
        (f"osh_finney_{_avenida}", "sur", f"osh_matheson_{_avenida}", "norte"),
        (f"osh_matheson_{_avenida}", "sur", f"osh_ellroy_{_avenida}", "norte"),
        (f"osh_ellroy_{_avenida}", "sur", f"osh_bloch_{_avenida}", "norte"),
    ]

del _calle, _avenida

# --- Old Silent Hill: callejones, puente e interiores ---------------------
CONEXIONES += [
    ("osh_finney_bachman", "norte", "osh_bachman_norte", "sur"),
    ("osh_finney_levin", "dentro", "osh_callejon_basket", "fuera"),
    ("osh_matheson_bradbury", "dentro", "osh_callejon_gordon", "fuera"),
    ("osh_callejon_gordon", "norte", "int_casa_gordon", "sur"),

    ("osh_finney_bachman", "café|cafe|5to2", "int_cafe_5to2", "fuera"),
    ("osh_finney_bachman", "tienda|kiosco", "int_tienda", "fuera"),
    ("osh_matheson_bachman", "queen|burger", "int_queen_burger", "fuera"),
    ("osh_matheson_levin", "casa", "int_casa_levin", "fuera"),
    ("osh_bloch_levin", "iglesia", "int_iglesia_balkan", "fuera"),
    ("osh_bloch_bradbury", "cutrite|motosierras", "int_cut_rite", "fuera"),
    ("osh_ellroy_bachman", "taller|estación|estacion", "int_estacion_servicio", "fuera"),

    ("osh_ellroy_midwich", "escuela|portón|porton", "esc_entrada", "fuera"),

    ("osh_bloch_bachman", "este", "osh_puente_levadizo", "oeste"),
    ("osh_puente_levadizo", "torre|control", "osh_torre_control", "fuera"),
    ("osh_puente_levadizo", "este", "csh_cabecera_puente", "oeste"),
]

# --- Escuela Midwich ------------------------------------------------------
CONEXIONES += [
    ("esc_entrada", "dentro", "esc_recepcion", "fuera"),
    ("esc_recepcion", "enfermería|enfermeria", "esc_enfermeria", "fuera"),
    ("esc_recepcion", "norte", "esc_patio", "sur"),
    ("esc_patio", "torre|reloj", "esc_torre_reloj", "fuera"),
    ("esc_patio", "oeste", "esc_pasillo_pb_izq", "este"),
    ("esc_patio", "este", "esc_pasillo_pb_der", "oeste"),
    ("esc_pasillo_pb_der", "aula", "esc_aula_pb", "fuera"),
    ("esc_pasillo_pb_izq", "abajo", "esc_caldera", "arriba"),
    ("esc_pasillo_pb_izq", "arriba", "esc_pasillo_1p_izq", "abajo"),
    ("esc_pasillo_1p_izq", "este", "esc_lab_quimica", "oeste"),
    ("esc_pasillo_1p_izq", "sur", "esc_sala_musica", "norte"),
    ("esc_pasillo_1p_izq", "norte", "esc_biblioteca", "sur"),
    ("esc_biblioteca", "depósito|deposito|reserva", "esc_reserva", "fuera"),
    ("esc_pasillo_1p_izq", "arriba", "esc_azotea", "abajo"),
]

# --- Central Silent Hill: grilla ------------------------------------------
for _calle in ("crichton", "koontz", "munson", "katz"):
    CONEXIONES += [
        (f"csh_{_calle}_simmons", "este", f"csh_{_calle}_sagan", "oeste"),
        (f"csh_{_calle}_sagan", "este", f"csh_{_calle}_bachman", "oeste"),
    ]
for _avenida in ("simmons", "sagan", "bachman"):
    CONEXIONES += [
        (f"csh_crichton_{_avenida}", "sur", f"csh_koontz_{_avenida}", "norte"),
        (f"csh_koontz_{_avenida}", "sur", f"csh_munson_{_avenida}", "norte"),
        (f"csh_munson_{_avenida}", "sur", f"csh_katz_{_avenida}", "norte"),
    ]
del _calle, _avenida

# --- Central Silent Hill: accesos e interiores ----------------------------
CONEXIONES += [
    ("csh_cabecera_puente", "este", "csh_koontz_simmons", "oeste"),
    ("csh_crichton_bachman", "antigüedades|antiguedades|green", "int_green_lion", "fuera"),
    ("csh_crichton_sagan", "comisaría|comisaria", "int_comisaria", "fuera"),
    ("csh_koontz_simmons", "café|cafe|sun", "int_cafe_sun", "fuera"),
    ("csh_munson_simmons", "mall|centro", "int_town_center", "fuera"),
    ("csh_koontz_sagan", "hospital", "hos_patio", "fuera"),
    ("csh_katz_sagan", "abajo", "alc_entrada", "arriba"),
    ("csh_katz_bachman", "sur", "res_bachman", "norte"),
]

# --- Hospital Alchemilla --------------------------------------------------
CONEXIONES += [
    ("hos_patio", "dentro", "hos_recepcion", "fuera"),
    ("hos_recepcion", "oeste", "hos_oficina", "este"),
    ("hos_recepcion", "este", "hos_examen", "oeste"),
    ("hos_examen", "norte", "hos_farmacia", "sur"),
    ("hos_farmacia", "este", "hos_consultorio", "oeste"),
    ("hos_consultorio", "norte", "hos_reuniones", "sur"),
    ("hos_recepcion", "norte", "hos_cocina", "sur"),
    ("hos_cocina", "oeste", "hos_direccion", "este"),
    ("hos_recepcion", "ascensor", "hos_ascensor", "fuera"),
    ("hos_recepcion", "abajo", "hos_escalera_sotano", "arriba"),
    ("hos_escalera_sotano", "abajo", "hos_generador", "arriba"),
    ("hos_ascensor", "arriba", "hos_pasillo_2", "abajo"),
    ("hos_pasillo_2", "arriba", "hos_pasillo_3", "abajo"),
]

# --- Alcantarillas --------------------------------------------------------
CONEXIONES += [
    ("alc_entrada", "sur", "alc_tunel_norte", "norte"),
    ("alc_tunel_norte", "sur", "alc_cruce", "norte"),
    ("alc_cruce", "oeste", "alc_oficina", "este"),
    ("alc_cruce", "arriba", "alc_nivel_superior", "abajo"),
    ("alc_cruce", "sur", "alc_tunel_sur", "norte"),
    ("alc_tunel_sur", "sur", "alc_salida", "norte"),
    ("alc_salida", "arriba", "res_craig", "abajo"),
]

# --- Área turística y parque ----------------------------------------------
CONEXIONES += [
    ("res_bachman", "sur", "res_craig", "norte"),
    ("res_bachman", "este", "res_entrada_parque", "oeste"),
    ("res_craig", "sur", "res_weaver", "norte"),
    ("res_craig", "oeste", "res_nathan", "este"),
    ("res_nathan", "sur", "res_bartlett", "norte"),
    # Sandford queda al sur de Weaver, no al oeste: así la traza cierra sobre
    # la grilla del mapa sin que dos calles se pisen en la misma celda.
    ("res_weaver", "sur", "res_sandford", "norte"),
    ("res_sandford", "oeste", "res_puente_sandford", "este"),
    ("res_puente_sandford", "oeste", "res_muelle", "este"),
    ("res_muelle", "norte", "res_faro", "sur"),

    ("res_craig", "bar|annies", "int_annies_bar", "fuera"),
    ("res_weaver", "librería|libreria|indian", "int_indian_runner", "fuera"),
    ("res_weaver", "motel", "int_motel_recepcion", "fuera"),
    ("int_motel_recepcion", "habitación|habitacion", "int_motel_hab3", "fuera"),
    ("int_motel_recepcion", "garage|garaje", "int_motel_garage", "fuera"),
    ("res_nathan", "bowling|bowl", "int_bowl_o_rama", "fuera"),
    ("res_bartlett", "hotel|lakeview", "int_hotel_lakeview", "fuera"),

    ("res_entrada_parque", "dentro", "par_explanada", "fuera"),
    ("par_explanada", "norte", "par_calesita", "sur"),
    ("par_explanada", "este", "par_vuelta_al_mundo", "oeste"),
    ("par_explanada", "oeste", "par_montana_rusa", "este"),
    ("par_vuelta_al_mundo", "heladería|heladeria", "par_heladeria", "fuera"),
]
