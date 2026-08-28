# -*- coding: utf-8 -*-
"""
Construye (y reconstruye) Nébrida desde `nebrida.py` y `ubicaciones.py`.

Uso desde el juego, como superusuario::

    batchcode batch.nebrida

Uso desde la línea de comandos::

    docker compose exec game evennia shell -c "from world.mapa.constructor import construir; construir()"

Es idempotente: cada corrida borra lo que dejó la corrida anterior y levanta
todo de cero. Solo toca objetos con la etiqueta del mapa, así que lo que hayas
creado a mano dentro de una sala se pierde junto con la sala, pero nada de
afuera del mapa se ve afectado.

Cómo se arma la ciudad:

1. `ubicaciones.py` dibuja cada plano como una imagen de texto, un carácter por
   celda.
2. **Lo transitable** —calles, plazas, parques, baldíos, la costa— es una sala
   por celda, y cada una se conecta con sus vecinas ortogonales.
3. **Lo construido** no se atraviesa. De cada grupo de celdas contiguas del
   mismo tipo se hace sala una sola: la de la puerta, el umbral donde se para
   quien va a entrar. Se llega a ella caminando desde la vereda, como a
   cualquier otra celda; el resto del edificio se dibuja pero es macizo, y
   desde la calle no hay salida hacia él.
4. Las celdas que reclama `NOMBRADAS` usan el nombre y la descripción escritos
   en `nebrida.py`. Si caen sobre un edificio, esa celda pasa a ser su puerta.
   Las demás se llenan con salas genéricas según su tipo y, si son calle, con
   el nombre de la calle.
"""

import os
from collections import defaultdict, deque

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from evennia.objects.models import ObjectDB
from evennia.objects.objects import DefaultExit, DefaultRoom
from evennia.utils import create, search

from world.mapa import iconos
from world.mapa import nebrida as datos
from world.mapa import ubicaciones

TAG_MAPA = "nebrida"
TAG_CATEGORIA = "mapa"

SALAS_EJEMPLO = ("Limbo",)

ARCHIVO_GENERADO = os.path.join(
    settings.GAME_DIR, "server", "conf", "mapa_generado.py"
)

# Vecinos ortogonales: dirección -> desplazamiento en (x, y).
VECINOS = {
    "norte": (0, 1),
    "sur": (0, -1),
    "este": (1, 0),
    "oeste": (-1, 0),
}

# Vecinos en diagonal. Solo se usan para las celdas de tipo "diagonal": una
# avenida en oblicuo avanza una celda en cada eje por paso, así que sus tramos
# se tocan en la esquina y no de lado. Se la podría ensanchar en escalera para
# que la grilla ortogonal la uniera, pero entonces se dibuja doble. Es una
# calle diagonal: se camina en diagonal.
DIAGONALES = {
    "noreste": (1, 1),
    "suroeste": (-1, -1),
    "noroeste": (-1, 1),
    "sureste": (1, -1),
}


# --------------------------------------------------------------------------
# Lectura de la traza
# --------------------------------------------------------------------------


def _transitables(celdas):
    """Celdas por las que se camina libremente: ni agua, ni bosque, ni edificio."""
    return {
        pos: tipo
        for pos, tipo in celdas.items()
        if tipo not in iconos.INTRANSITABLES and tipo not in iconos.CONSTRUCCIONES
    }


def _vecinas_de(pos):
    plano, x, y, z = pos
    for direccion, (dx, dy) in VECINOS.items():
        yield direccion, (plano, x + dx, y + dy, z)


def _vecinas_diagonales(pos):
    plano, x, y, z = pos
    for direccion, (dx, dy) in DIAGONALES.items():
        yield direccion, (plano, x + dx, y + dy, z)


def _une_diagonal(transitables, a, b):
    """
    True si dos celdas en diagonal se comunican.

    Solo cuando alguna de las dos es la avenida diagonal: el resto de la ciudad
    se camina en cruz, como corresponde a un damero.

    """
    return "diagonal" in (transitables.get(a), transitables.get(b))


def _grupos_construidos(celdas):
    """
    Agrupa en edificios las celdas construidas contiguas del mismo tipo.

    Returns:
        list: tuplas `(tipo, set de posiciones)`.

    """
    pendientes = {
        pos: tipo for pos, tipo in celdas.items() if tipo in iconos.CONSTRUCCIONES
    }
    grupos = []
    while pendientes:
        semilla, tipo = next(iter(pendientes.items()))
        grupo = set()
        cola = deque([semilla])
        while cola:
            pos = cola.popleft()
            if pendientes.get(pos) != tipo:
                continue
            del pendientes[pos]
            grupo.add(pos)
            for _dir, vecina in _vecinas_de(pos):
                cola.append(vecina)
        grupos.append((tipo, grupo))
    return grupos


def _elegir_puertas(grupos, transitables, reclamadas):
    """
    Elige, para cada edificio, la celda que hace de puerta.

    Si una sala escrita reclamó una celda del edificio, esa es la puerta: a la
    catedral se entra por la catedral. Si no, la primera celda que dé a un
    lugar transitable, en un orden fijo para que dos corridas den lo mismo.

    Returns:
        tuple: `(puertas, sin_salida)`. `puertas` es
        `{pos: (tipo, calle, celdas_del_edificio)}`; `sin_salida` son los
        edificios que no tocan nada caminable.

    """
    puertas = {}
    sin_salida = []
    # Una celda de calle no puede tener dos salidas `entrar`: el nombre choca y
    # la segunda no se crea, dejando un edificio sin acceso. Así que cada
    # puerta se lleva su propio tramo de vereda.
    calles_tomadas = set()
    for tipo, grupo in sorted(grupos, key=lambda g: min(g[1])):
        candidatas = [
            (pos, calle)
            for pos in sorted(grupo)
            for _dir, calle in _vecinas_de(pos)
            if calle in transitables
        ]
        if not candidatas:
            sin_salida.append((tipo, min(grupo)))
            continue
        preferidas = [c for c in candidatas if c[0] in reclamadas]
        libres = [c for c in (preferidas or candidatas) if c[1] not in calles_tomadas]
        if not libres:
            # Todas las veredas que toca ya son puerta de otro edificio. Con
            # manzanas de dos y tres celdas esto no debería pasar; si pasa, se
            # avisa en vez de dejar el edificio mudo.
            sin_salida.append((tipo, min(grupo)))
            continue
        pos, calle = libres[0]
        calles_tomadas.add(calle)
        puertas[pos] = (tipo, calle, len(grupo))
    return puertas, sin_salida


# --------------------------------------------------------------------------
# Validación
# --------------------------------------------------------------------------


def validar():
    """
    Revisa los datos antes de tocar la base.

    Returns:
        list: mensajes de error. Vacía si todo cierra.

    """
    errores = []

    try:
        celdas = ubicaciones.todas_las_celdas()
    except ValueError as err:
        return [str(err)]

    transitables = _transitables(celdas)
    reclamadas = set(ubicaciones.NOMBRADAS.values())
    grupos = _grupos_construidos(celdas)
    puertas, sin_salida = _elegir_puertas(grupos, transitables, reclamadas)

    for tipo, pos in sin_salida:
        errores.append(
            f"el edificio de tipo '{tipo}' que empieza en {pos} se queda sin "
            "puerta: o no toca ninguna calle, o las que toca ya son puerta de "
            "otro edificio"
        )

    faltan = {t for t in transitables.values() if t not in ubicaciones.RELLENO}
    for tipo in sorted(faltan):
        errores.append(f"el tipo '{tipo}' no tiene entrada en RELLENO")
    faltan = {t for t, _c, _n in puertas.values() if t not in ubicaciones.ENTRADAS}
    for tipo in sorted(faltan):
        errores.append(f"el tipo construido '{tipo}' no tiene entrada en ENTRADAS")

    # --- las salas con nombre caen donde se puede estar, y una sola por celda
    ocupadas = {}
    for clave, pos in ubicaciones.NOMBRADAS.items():
        if clave not in datos.SALAS:
            errores.append(f"NOMBRADAS tiene '{clave}', que no existe en SALAS")
            continue
        if pos not in celdas:
            errores.append(f"'{clave}' apunta a la celda {pos}, que no está dibujada")
        elif pos not in transitables and pos not in puertas:
            tipo = celdas[pos]
            motivo = (
                "no se camina"
                if tipo in iconos.INTRANSITABLES
                else "está dentro de un edificio y no es su puerta"
            )
            errores.append(f"'{clave}' cae en {pos}, que {motivo} ('{tipo}')")
        elif pos in ocupadas:
            errores.append(f"'{clave}' y '{ocupadas[pos]}' se pelean la celda {pos}")
        else:
            ocupadas[pos] = clave

    for clave in datos.SALAS:
        en_grilla = clave in ubicaciones.NOMBRADAS
        anclada = clave in ubicaciones.ANCLADAS
        if not en_grilla and not anclada:
            errores.append(f"la sala '{clave}' no está ni en NOMBRADAS ni en ANCLADAS")
        elif en_grilla and anclada:
            errores.append(f"la sala '{clave}' está en NOMBRADAS y en ANCLADAS")
    for clave in ubicaciones.ANCLADAS:
        if clave not in datos.SALAS:
            errores.append(f"ANCLADAS tiene '{clave}', que no existe en SALAS")

    # --- las conexiones a mano son coherentes ---
    salidas = defaultdict(dict)
    for i, conexion in enumerate(datos.CONEXIONES):
        if len(conexion) != 4:
            errores.append(
                f"conexión {i}: se esperaban 4 elementos, hay {len(conexion)}"
            )
            continue
        a, ida, b, vuelta = conexion
        for clave in (a, b):
            if clave not in datos.SALAS:
                errores.append(f"conexión {i}: la sala '{clave}' no existe en SALAS")
        for origen, nombre, destino in ((a, ida, b), (b, vuelta, a)):
            if nombre is None:
                continue
            principal = nombre.split("|")[0]
            if principal in salidas[origen]:
                errores.append(
                    f"salida duplicada '{principal}' en '{origen}': "
                    f"apunta a '{salidas[origen][principal]}' y a '{destino}'"
                )
            salidas[origen][principal] = destino

    if datos.SALA_INICIO not in datos.SALAS:
        errores.append(f"SALA_INICIO '{datos.SALA_INICIO}' no existe en SALAS")

    if errores:
        return errores

    # --- todo es alcanzable a pie desde el punto de partida ---
    #     El umbral de cada edificio es una sala más: se llega caminando.
    caminables = dict(transitables)
    caminables.update({pos: tipo for pos, (tipo, _c, _n) in puertas.items()})

    por_celda = dict(ocupadas)
    for pos in caminables:
        por_celda.setdefault(pos, f"libre{pos}")

    grafo = defaultdict(set)
    for origen, destinos in salidas.items():
        grafo[origen].update(destinos.values())
    # la grilla solo conecta lo transitable entre sí
    for pos in transitables:
        for _dir, vecina in _vecinas_de(pos):
            if vecina in transitables:
                grafo[por_celda[pos]].add(por_celda[vecina])
                grafo[por_celda[vecina]].add(por_celda[pos])
    # la avenida diagonal, en oblicuo
    for pos in transitables:
        for _dir, vecina in _vecinas_diagonales(pos):
            if vecina in transitables and _une_diagonal(transitables, pos, vecina):
                grafo[por_celda[pos]].add(por_celda[vecina])
                grafo[por_celda[vecina]].add(por_celda[pos])

    # cada puerta, con su calle
    for pos, (_tipo, calle, _n) in puertas.items():
        grafo[por_celda[pos]].add(por_celda[calle])
        grafo[por_celda[calle]].add(por_celda[pos])

    vistas = {datos.SALA_INICIO}
    cola = deque([datos.SALA_INICIO])
    while cola:
        actual = cola.popleft()
        for destino in grafo[actual]:
            if destino not in vistas:
                vistas.add(destino)
                cola.append(destino)

    for clave in sorted(set(por_celda.values()) | set(datos.SALAS)):
        if clave not in vistas:
            errores.append(f"'{clave}' no es alcanzable caminando desde SALA_INICIO")

    return errores


# --------------------------------------------------------------------------
# Construcción
# --------------------------------------------------------------------------


def _alias_de(nombre):
    """Parte "café|cafe|5to2" en ("café", ["cafe", "5to2"]) y suma direcciones."""
    partes = nombre.split("|")
    clave, alias = partes[0], partes[1:]
    alias += list(datos.DIRECCIONES.get(clave, ()))
    return clave, alias


def _escribir_generado(sala_inicio):
    """Deja los dbref resultantes donde settings.py los pueda leer."""
    lineas = [
        "# -*- coding: utf-8 -*-",
        '"""',
        "Generado por world.mapa.constructor. NO EDITAR A MANO.",
        "",
        "Los dbref son propios de esta base de datos, por eso el archivo no se",
        "versiona: se regenera cada vez que se reconstruye el mapa. Los cambios",
        "acá necesitan reiniciar el server, no alcanza con un reload:",
        "",
        "    docker compose restart game",
        '"""',
        "",
        f'START_LOCATION = "#{sala_inicio.id}"',
        f'DEFAULT_HOME = "#{sala_inicio.id}"',
        "",
    ]
    with open(ARCHIVO_GENERADO, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lineas))


def _vecinos_trama(celdas, plano, x, y, z):
    """
    Por cuáles de los cuatro lados sigue la trama de calles.

    Es lo que decide con qué carácter se dibuja el tramo: una calle que sigue
    al norte y al este es una esquina `└`; la que sigue en las cuatro
    direcciones, un cruce `┼`. No se declara en los datos porque se deduce sin
    ambigüedad del dibujo, y un dato que se puede deducir es un dato que se
    puede contradecir.

    """
    return tuple(
        1 if celdas.get((plano, x + dx, y + dy, z)) in iconos.TRAMA else 0
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
    )


def _relleno_para(tipo, plano, x, y, z):
    """
    Nombre y descripción de una sala que nadie reclamó.

    Las calles se llaman como la calle: es lo que hace que caminar por Nébrida
    se sienta como caminar por una ciudad y no por una grilla. El resto elige
    una de las variantes de su tipo, siempre la misma para la misma celda.

    """
    variantes = ubicaciones.RELLENO[tipo]
    nombre, desc = variantes[(x * 7 + y * 13 + z) % len(variantes)]
    if tipo in iconos.TRAMA and plano == "nebrida":
        calle = ubicaciones.nombre_de_calle(x, y)
        if calle:
            nombre = calle
    return nombre, desc


def _crear_sala(
    key, desc, tipo, plano=None, pos=None, vecinos=None, puerta=False,
    senalar=False,
):
    """Crea una sala del mapa con sus atributos de grilla."""
    atributos = [("desc", desc), ("tipo_mapa", tipo)]
    etiquetas = [(TAG_MAPA, TAG_CATEGORIA), (tipo, "tipo_mapa")]
    if vecinos:
        atributos.append(("vecinos_trama", vecinos))
    if puerta:
        atributos.append(("es_puerta", True))
        etiquetas.append(("puerta", "mapa"))
    if senalar:
        # Solo los edificios que ocupan varias celdas señalan su puerta en el
        # mapa. En uno de una sola celda, el `+` taparía de qué edificio se
        # trata para decir algo que ya es evidente.
        atributos.append(("puerta_visible", True))
    if plano is not None:
        atributos += [("plano", plano), ("pos", pos)]
        etiquetas.append((plano, "plano"))
    return create.create_object(
        settings.BASE_ROOM_TYPECLASS,
        key=key,
        attributes=atributos,
        tags=etiquetas,
        # Una sala no vive dentro de nada, y pedir home obligaría a resolver
        # settings.DEFAULT_HOME, que en este punto todavía puede apuntar a una
        # sala que esta misma corrida va a borrar.
        nohome=True,
    )


def construir(caller=None, borrar_ejemplos=True):
    """
    Borra la ciudad anterior y la reconstruye desde los datos.

    Args:
        caller (Object, optional): si viene, se le informan los pasos in-game.
        borrar_ejemplos (bool): además elimina las salas de ejemplo de Evennia.

    Returns:
        dict: resumen de lo construido.

    """

    def informar(texto):
        if caller:
            caller.msg(texto)
        else:
            print(texto)

    errores = validar()
    if errores:
        informar("|rLa ciudad tiene errores. No se construyó nada.|n")
        for err in errores[:40]:
            informar(f"  - {err}")
        return {"errores": errores}

    viejos = list(search.search_tag(TAG_MAPA, category=TAG_CATEGORIA))
    informar(f"Objetos de la ciudad anterior a reemplazar: |w{len(viejos)}|n")

    celdas = ubicaciones.todas_las_celdas()
    transitables = _transitables(celdas)
    nombrada_en = {pos: clave for clave, pos in ubicaciones.NOMBRADAS.items()}
    grupos = _grupos_construidos(celdas)
    puertas, _sin_salida = _elegir_puertas(grupos, transitables, set(nombrada_en))

    salas = {}       # clave de datos -> sala
    por_celda = {}   # (plano, x, y, z) -> sala
    escritas = relleno = 0

    # --- 1. Lo transitable: una sala por celda ----------------------------
    for pos, tipo in sorted(transitables.items()):
        plano, x, y, z = pos
        vecinos = (
            _vecinos_trama(celdas, plano, x, y, z) if tipo in iconos.TRAMA else None
        )
        clave = nombrada_en.get(pos)
        if clave:
            spec = datos.SALAS[clave]
            desc = spec["desc"]
            if spec.get("exterior"):
                desc = datos.NIEBLA + desc
            sala = _crear_sala(spec["nombre"], desc, tipo, plano, (x, y, z), vecinos)
            salas[clave] = sala
            escritas += 1
        else:
            nombre, desc = _relleno_para(tipo, plano, x, y, z)
            if tipo in ubicaciones.RELLENO_EXTERIOR:
                desc = datos.NIEBLA + desc
            sala = _crear_sala(nombre, desc, tipo, plano, (x, y, z), vecinos)
            relleno += 1
        por_celda[pos] = sala

    informar(f"Salas transitables: |w{escritas + relleno}|n")

    # --- 2. Las puertas: una sala por edificio ----------------------------
    for pos, (tipo, _calle, celdas_edificio) in sorted(puertas.items()):
        plano, x, y, z = pos
        clave = nombrada_en.get(pos)
        if clave:
            spec = datos.SALAS[clave]
            desc = spec["desc"]
            if spec.get("exterior"):
                desc = datos.NIEBLA + desc
            sala = _crear_sala(
                spec["nombre"], desc, tipo, plano, (x, y, z),
                puerta=True, senalar=celdas_edificio > 1,
            )
            salas[clave] = sala
            escritas += 1
        else:
            nombre, desc = ubicaciones.ENTRADAS[tipo]
            sala = _crear_sala(
                nombre, desc, tipo, plano, (x, y, z),
                puerta=True, senalar=celdas_edificio > 1,
            )
        por_celda[pos] = sala

    informar(f"Edificios: |w{len(grupos)}|n, cada uno con su puerta")

    # --- 3. Interiores sin celda propia -----------------------------------
    for clave, tipo in ubicaciones.ANCLADAS.items():
        spec = datos.SALAS[clave]
        desc = spec["desc"]
        if spec.get("exterior"):
            desc = datos.NIEBLA + desc
        salas[clave] = _crear_sala(spec["nombre"], desc, tipo)

    # --- 4. Salidas declaradas a mano -------------------------------------
    def crear_salida(origen, nombre, destino):
        clave, alias = _alias_de(nombre)
        if any(salida.key == clave for salida in origen.exits):
            return False
        create.create_object(
            settings.BASE_EXIT_TYPECLASS,
            key=clave,
            aliases=alias,
            location=origen,
            destination=destino,
            nohome=True,
            tags=[(TAG_MAPA, TAG_CATEGORIA)],
        )
        return True

    manuales = 0
    for a, ida, b, vuelta in datos.CONEXIONES:
        for origen, nombre, destino in (
            (salas[a], ida, salas[b]),
            (salas[b], vuelta, salas[a]),
        ):
            if nombre is not None and crear_salida(origen, nombre, destino):
                manuales += 1
    informar(f"Salidas escritas a mano: |w{manuales}|n")

    # --- 5. La grilla ------------------------------------------------------
    #        Se conecta lo transitable y también el umbral de cada edificio: al
    #        umbral se llega caminando desde la vereda, como a cualquier otra
    #        celda. Lo que queda afuera es el cuerpo del edificio, que no es
    #        sala; y dos umbrales nunca se conectan entre sí, porque si no se
    #        pasaría de un edificio al de al lado sin salir a la calle.
    caminables = dict(transitables)
    caminables.update({pos: tipo for pos, (tipo, _c, _n) in puertas.items()})
    automaticas = 0
    for pos in caminables:
        for direccion, vecina in _vecinas_de(pos):
            if (
                vecina in caminables
                and not (pos in puertas and vecina in puertas)
                and crear_salida(por_celda[pos], direccion, por_celda[vecina])
            ):
                automaticas += 1
    for pos in transitables:
        for direccion, vecina in _vecinas_diagonales(pos):
            if (
                vecina in transitables
                and _une_diagonal(transitables, pos, vecina)
                and crear_salida(por_celda[pos], direccion, por_celda[vecina])
            ):
                automaticas += 1
    informar(f"Salidas automáticas de la grilla: |w{automaticas}|n")

    # --- 6. Adentro, todavía nada -----------------------------------------
    #        El umbral tendría que tener una salida `entrar` hacia el interior
    #        del edificio, pero los interiores no están construidos y una
    #        salida sin destino no existe en Evennia. Crear ciento setenta y
    #        ocho salas idénticas que digan "está oscuro" solo para que el
    #        comando exista sería peor que no tenerlo: el umbral ya dice que
    #        hay una puerta y que del otro lado no se ve.
    #
    #        Cuando haya interiores, el `entrar` se agrega acá.

    inicio = salas[datos.SALA_INICIO]

    # --- 7. Salas de ejemplo de Evennia -----------------------------------
    ejemplos = []
    if borrar_ejemplos:
        for nombre in SALAS_EJEMPLO:
            for obj in search.search_object(nombre, exact=True):
                if obj not in por_celda.values() and obj.destination is None:
                    ejemplos.append(obj)

    condenadas = set(viejos) | set(ejemplos)

    # --- 8. Rescatar lo que esté parado sobre algo que va a desaparecer ---
    #        location=None no es un huérfano: es el estado normal de un
    #        personaje deslogueado, que Evennia saca del mundo hasta que su
    #        cuenta vuelva.
    mudados = 0
    for obj in ObjectDB.objects.all():
        if obj in condenadas or isinstance(obj, (DefaultRoom, DefaultExit)):
            continue
        if obj.location in condenadas:
            obj.location = inicio
            mudados += 1
        if obj.home in condenadas or obj.home is None:
            obj.home = inicio
        if obj.db.prelogout_location in condenadas:
            obj.db.prelogout_location = inicio
    if mudados:
        informar(f"Objetos y personajes mudados a la sala de inicio: |w{mudados}|n")

    # --- 9. Recién ahora, borrar ------------------------------------------
    #        Al borrar una sala se van con ella sus salidas, así que la mitad
    #        de esta lista ya no existe para cuando le llega el turno.
    borradas = 0
    for obj in condenadas:
        try:
            obj.delete()
            borradas += 1
        except ObjectDoesNotExist:
            pass
    informar(f"Objetos borrados: |w{borradas}|n")

    _escribir_generado(inicio)
    informar(
        f"\nEl juego arranca en |c{inicio.key}|n (|w#{inicio.id}|n).\n"
        "|yPara que el server tome el nuevo punto de partida hay que "
        "reiniciarlo:|n\n"
        "    docker compose restart game"
    )

    return {
        "salas": len(por_celda) + len(ubicaciones.ANCLADAS),
        "edificios": len(grupos),
        "salidas": manuales + automaticas,
        "borradas": borradas,
        "inicio": inicio,
    }
