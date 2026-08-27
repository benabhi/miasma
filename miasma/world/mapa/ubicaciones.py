# -*- coding: utf-8 -*-
"""
Dónde cae cada sala en el mapa, y con qué icono se dibuja.

Está separado de `silent_hill.py` a propósito: ahí van los nombres y las
descripciones, acá la geometría. Se pueden tocar por separado.

Dos formas de aparecer en el mapa:

`UBICACIONES`
    Salas con celda propia: `(plano, x, y, z, tipo)`. Un *plano* es un mapa
    independiente —el pueblo, la escuela, el hospital, las cloacas, el
    parque—; dentro de un plano, `x` crece hacia el este, `y` hacia el norte y
    `z` es el piso.

`ANCLADAS`
    Interiores de una sola sala: `tipo`. No ocupan celda. Dibujar un mapa de
    una celda para el interior de un bar no le sirve a nadie, así que cuando el
    jugador está adentro el minimapa muestra la calle de la que se entra, con
    la marca del jugador sobre esa celda. El constructor resuelve el ancla
    sola, mirando de dónde se entra.

Los edificios que sí tienen varias salas (escuela, hospital, cloacas, parque)
tienen su propio plano y se recorren con su propio mapa.
"""

# --------------------------------------------------------------------------
# EL PUEBLO
#
# Un solo plano continuo, de Old Silent Hill al lago. La grilla de calles:
#
#     Old Silent Hill          Central              Área turística
#     x: Bradbury 0            x: Simmons  6        x: 6..9
#        Midwich  1               Sagan    7        y: 0..3
#        Levin    2               Bachman  8
#        Bachman  3            y: Katz     4
#     y: Bloch    6               Munson   5
#        Ellroy   7               Koontz   6
#        Matheson 8               Crichton 7
#        Finney   9
#
# El tipo de cada cruce es el del lugar que lo define: la esquina del café es
# "comercio", la que da al paredón de la escuela es "escuela". No es que la
# calle sea un negocio: es que en el mapa lo que importa es qué hay ahí.
# --------------------------------------------------------------------------

UBICACIONES = {
    # --- Old Silent Hill ---------------------------------------------------
    "osh_finney_bradbury": ("pueblo", 0, 9, 0, "descampado"),
    "osh_finney_midwich": ("pueblo", 1, 9, 0, "calle"),
    "osh_finney_levin": ("pueblo", 2, 9, 0, "casa"),
    "osh_finney_bachman": ("pueblo", 3, 9, 0, "comercio"),
    "osh_matheson_bradbury": ("pueblo", 0, 8, 0, "descampado"),
    "osh_matheson_midwich": ("pueblo", 1, 8, 0, "calle"),
    "osh_matheson_levin": ("pueblo", 2, 8, 0, "casa"),
    "osh_matheson_bachman": ("pueblo", 3, 8, 0, "comercio"),
    "osh_ellroy_bradbury": ("pueblo", 0, 7, 0, "descampado"),
    "osh_ellroy_midwich": ("pueblo", 1, 7, 0, "escuela"),
    "osh_ellroy_levin": ("pueblo", 2, 7, 0, "industria"),
    "osh_ellroy_bachman": ("pueblo", 3, 7, 0, "industria"),
    "osh_bloch_bradbury": ("pueblo", 0, 6, 0, "comercio"),
    "osh_bloch_midwich": ("pueblo", 1, 6, 0, "escuela"),
    "osh_bloch_levin": ("pueblo", 2, 6, 0, "iglesia"),
    "osh_bloch_bachman": ("pueblo", 3, 6, 0, "avenida"),
    "osh_bachman_norte": ("pueblo", 3, 10, 0, "descampado"),
    "osh_callejon_basket": ("pueblo", 2, 10, 0, "callejon"),
    "osh_callejon_gordon": ("pueblo", -1, 8, 0, "callejon"),
    "osh_puente_levadizo": ("pueblo", 4, 6, 0, "puente"),
    # --- Central Silent Hill -----------------------------------------------
    "csh_cabecera_puente": ("pueblo", 5, 6, 0, "puente"),
    "csh_crichton_simmons": ("pueblo", 6, 7, 0, "calle"),
    "csh_crichton_sagan": ("pueblo", 7, 7, 0, "comisaria"),
    "csh_crichton_bachman": ("pueblo", 8, 7, 0, "comercio"),
    "csh_koontz_simmons": ("pueblo", 6, 6, 0, "comercio"),
    "csh_koontz_sagan": ("pueblo", 7, 6, 0, "hospital"),
    "csh_koontz_bachman": ("pueblo", 8, 6, 0, "edificio"),
    "csh_munson_simmons": ("pueblo", 6, 5, 0, "edificio"),
    "csh_munson_sagan": ("pueblo", 7, 5, 0, "edificio"),
    "csh_munson_bachman": ("pueblo", 8, 5, 0, "edificio"),
    "csh_katz_simmons": ("pueblo", 6, 4, 0, "descampado"),
    "csh_katz_sagan": ("pueblo", 7, 4, 0, "alcantarilla"),
    "csh_katz_bachman": ("pueblo", 8, 4, 0, "avenida"),
    # --- Área turística ----------------------------------------------------
    "res_bachman": ("pueblo", 8, 3, 0, "avenida"),
    "res_craig": ("pueblo", 8, 2, 0, "comercio"),
    "res_weaver": ("pueblo", 8, 1, 0, "casa"),
    "res_nathan": ("pueblo", 7, 2, 0, "avenida"),
    "res_bartlett": ("pueblo", 7, 1, 0, "hotel"),
    "res_sandford": ("pueblo", 8, 0, 0, "calle"),
    "res_puente_sandford": ("pueblo", 7, 0, 0, "puente"),
    "res_muelle": ("pueblo", 6, 0, 0, "muelle"),
    "res_faro": ("pueblo", 6, 1, 0, "faro"),
    "res_entrada_parque": ("pueblo", 9, 3, 0, "atraccion"),
    # --- Escuela Midwich ---------------------------------------------------
    "esc_entrada": ("escuela", 1, 0, 0, "calle"),
    "esc_recepcion": ("escuela", 1, 1, 0, "interior"),
    "esc_patio": ("escuela", 1, 2, 0, "descampado"),
    "esc_pasillo_pb_izq": ("escuela", 0, 2, 0, "pasillo"),
    "esc_pasillo_pb_der": ("escuela", 2, 2, 0, "pasillo"),
    "esc_caldera": ("escuela", 0, 2, -1, "sotano"),
    "esc_pasillo_1p_izq": ("escuela", 0, 2, 1, "pasillo"),
    "esc_lab_quimica": ("escuela", 1, 2, 1, "sala"),
    "esc_sala_musica": ("escuela", 0, 1, 1, "sala"),
    "esc_biblioteca": ("escuela", 0, 3, 1, "sala"),
    "esc_azotea": ("escuela", 0, 2, 2, "azotea"),
    # --- Hospital Alchemilla -----------------------------------------------
    "hos_patio": ("hospital", 1, 0, 0, "calle"),
    "hos_recepcion": ("hospital", 1, 1, 0, "interior"),
    "hos_oficina": ("hospital", 0, 1, 0, "sala"),
    "hos_examen": ("hospital", 2, 1, 0, "sala"),
    "hos_farmacia": ("hospital", 2, 2, 0, "sala"),
    "hos_consultorio": ("hospital", 3, 2, 0, "sala"),
    "hos_reuniones": ("hospital", 3, 3, 0, "sala"),
    "hos_cocina": ("hospital", 1, 2, 0, "sala"),
    "hos_direccion": ("hospital", 0, 2, 0, "sala"),
    "hos_ascensor": ("hospital", 2, 0, 0, "escalera"),
    "hos_pasillo_2": ("hospital", 2, 0, 1, "pasillo"),
    "hos_pasillo_3": ("hospital", 2, 0, 2, "pasillo"),
    "hos_escalera_sotano": ("hospital", 1, 1, -1, "escalera"),
    "hos_generador": ("hospital", 1, 1, -2, "sotano"),
    # --- Alcantarillas -----------------------------------------------------
    "alc_entrada": ("cloacas", 1, 4, -1, "escalera"),
    "alc_tunel_norte": ("cloacas", 1, 3, -1, "alcantarilla"),
    "alc_cruce": ("cloacas", 1, 2, -1, "alcantarilla"),
    "alc_oficina": ("cloacas", 0, 2, -1, "sala"),
    "alc_nivel_superior": ("cloacas", 1, 2, 0, "alcantarilla"),
    "alc_tunel_sur": ("cloacas", 1, 1, -1, "alcantarilla"),
    "alc_salida": ("cloacas", 1, 0, -1, "escalera"),
    # --- Lakeside Amusement Park -------------------------------------------
    "par_explanada": ("parque", 1, 1, 0, "descampado"),
    "par_calesita": ("parque", 1, 2, 0, "atraccion"),
    "par_vuelta_al_mundo": ("parque", 2, 1, 0, "atraccion"),
    "par_montana_rusa": ("parque", 0, 1, 0, "atraccion"),
}

# --------------------------------------------------------------------------
# Interiores de una sola sala. No ocupan celda: el minimapa muestra de dónde
# se entró. El tipo se usa igual, para el icono del jugador y la leyenda.
# --------------------------------------------------------------------------

ANCLADAS = {
    "int_cafe_5to2": "comercio",
    "int_tienda": "comercio",
    "int_queen_burger": "comercio",
    "int_casa_levin": "casa",
    "int_casa_gordon": "casa",
    "int_iglesia_balkan": "iglesia",
    "int_cut_rite": "comercio",
    "int_estacion_servicio": "industria",
    "osh_torre_control": "industria",
    "int_comisaria": "comisaria",
    "int_green_lion": "comercio",
    "int_cafe_sun": "comercio",
    "int_town_center": "edificio",
    "int_annies_bar": "comercio",
    "int_indian_runner": "comercio",
    "int_motel_recepcion": "hotel",
    "int_motel_hab3": "interior",
    "int_motel_garage": "industria",
    "int_bowl_o_rama": "comercio",
    "int_hotel_lakeview": "hotel",
    "esc_enfermeria": "sala",
    "esc_aula_pb": "sala",
    "esc_torre_reloj": "interior",
    "esc_reserva": "sala",
    "par_heladeria": "comercio",
}

# Nombre legible de cada plano, para el encabezado del mapa.
NOMBRES_PLANO = {
    "pueblo": "Silent Hill",
    "escuela": "Escuela Midwich",
    "hospital": "Hospital Alchemilla",
    "cloacas": "Alcantarillas",
    "parque": "Lakeside Amusement Park",
}
