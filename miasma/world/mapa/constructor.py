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

Cómo se arma el mundo:

1. `ubicaciones.py` dibuja cada plano como una imagen de texto, un carácter por
   celda. Toda celda transitable es una sala.
2. Las celdas que reclama `NOMBRADAS` usan el nombre y la descripción escritos
   en `nebrida.py`. Las demás se llenan con salas genéricas según su tipo y,
   si son calle, con el nombre de la calle,
   para que la grilla quede densa sin escribir doscientas descripciones.
3. Cada sala se conecta automáticamente con sus vecinas ortogonales. Las
   salidas declaradas a mano en `CONEXIONES` tienen prioridad: la conexión
   automática nunca pisa una salida que ya existe con ese nombre.
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

    transitables = {
        pos: tipo
        for pos, tipo in celdas.items()
        if tipo not in iconos.INTRANSITABLES
    }

    # --- toda celda transitable tiene con qué rellenarse ---
    for tipo in sorted({t for t in transitables.values() if t not in ubicaciones.RELLENO}):
        errores.append(f"el tipo '{tipo}' no tiene entrada en RELLENO")

    # --- las salas con nombre caen en una celda transitable, y una sola ---
    ocupadas = {}
    for clave, pos in ubicaciones.NOMBRADAS.items():
        if clave not in datos.SALAS:
            errores.append(f"NOMBRADAS tiene '{clave}', que no existe en SALAS")
            continue
        if pos not in celdas:
            errores.append(f"'{clave}' apunta a la celda {pos}, que no está dibujada")
        elif pos not in transitables:
            errores.append(
                f"'{clave}' cae en {pos}, que es '{celdas[pos]}' y no se camina"
            )
        elif pos in ocupadas:
            errores.append(f"'{clave}' y '{ocupadas[pos]}' se pelean la celda {pos}")
        else:
            ocupadas[pos] = clave

    # --- toda sala escrita está ubicada, de una forma o de la otra ---
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

    # --- todo el mundo es alcanzable a pie desde el punto de partida ---
    #     Se arma el grafo completo: las conexiones a mano más las automáticas
    #     entre celdas vecinas.
    por_celda = dict(ocupadas)
    for pos in transitables:
        por_celda.setdefault(pos, f"relleno{pos}")

    grafo = defaultdict(set)
    for origen, destinos in salidas.items():
        grafo[origen].update(destinos.values())
    for (plano, x, y, z), clave in por_celda.items():
        for dx, dy in VECINOS.values():
            vecina = por_celda.get((plano, x + dx, y + dy, z))
            if vecina:
                grafo[clave].add(vecina)
                grafo[vecina].add(clave)

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
    al norte y al este es una esquina `└`, la que sigue en las cuatro
    direcciones es un cruce `┼`. No se declara en los datos porque se deduce
    sin ambigüedad del dibujo, y un dato que se puede deducir es un dato que se
    puede contradecir.

    Returns:
        tuple: `(norte, sur, este, oeste)` con 1 donde sigue la trama.

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


def _crear_sala(key, desc, tipo, plano=None, pos=None, vecinos=None):
    """Crea una sala del mapa con sus atributos de grilla."""
    atributos = [("desc", desc), ("tipo_mapa", tipo)]
    etiquetas = [(TAG_MAPA, TAG_CATEGORIA), (tipo, "tipo_mapa")]
    if vecinos:
        atributos.append(("vecinos_trama", vecinos))
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
    Borra el mundo anterior y lo reconstruye desde los datos.

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
        informar("|rEl mundo tiene errores. No se construyó nada.|n")
        for err in errores:
            informar(f"  - {err}")
        return {"errores": errores}

    viejos = list(search.search_tag(TAG_MAPA, category=TAG_CATEGORIA))
    informar(f"Objetos del mundo anterior a reemplazar: |w{len(viejos)}|n")

    celdas = ubicaciones.todas_las_celdas()
    nombrada_en = {pos: clave for clave, pos in ubicaciones.NOMBRADAS.items()}

    salas = {}       # clave de datos -> sala
    por_celda = {}   # (plano, x, y, z) -> sala
    escritas = relleno = 0

    # --- 1. Una sala por celda transitable --------------------------------
    for pos, tipo in sorted(celdas.items()):
        if tipo in iconos.INTRANSITABLES:
            continue
        plano, x, y, z = pos
        vecinos = (
            _vecinos_trama(celdas, plano, x, y, z)
            if tipo in iconos.TRAMA
            else None
        )
        clave = nombrada_en.get(pos)
        if clave:
            spec = datos.SALAS[clave]
            desc = spec["desc"]
            if spec.get("exterior"):
                desc = datos.NIEBLA + desc
            sala = _crear_sala(
                spec["nombre"], desc, tipo, plano, (x, y, z), vecinos
            )
            salas[clave] = sala
            escritas += 1
        else:
            nombre, desc = _relleno_para(tipo, plano, x, y, z)
            if tipo in ubicaciones.RELLENO_EXTERIOR:
                desc = datos.NIEBLA + desc
            sala = _crear_sala(nombre, desc, tipo, plano, (x, y, z), vecinos)
            relleno += 1
        por_celda[pos] = sala

    informar(f"Salas con nombre propio: |w{escritas}|n")
    informar(f"Salas de relleno: |w{relleno}|n")

    # --- 2. Interiores sin celda propia -----------------------------------
    for clave, tipo in ubicaciones.ANCLADAS.items():
        spec = datos.SALAS[clave]
        desc = spec["desc"]
        if spec.get("exterior"):
            desc = datos.NIEBLA + desc
        salas[clave] = _crear_sala(spec["nombre"], desc, tipo)
    informar(f"Interiores sin celda: |w{len(ubicaciones.ANCLADAS)}|n")

    # --- 3. Salidas declaradas a mano -------------------------------------
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

    # --- 4. Conexión automática de la grilla ------------------------------
    #        Toda celda se comunica con sus vecinas ortogonales. Si ya había
    #        una salida con ese nombre —porque la declaró CONEXIONES— se
    #        respeta la escrita a mano.
    automaticas = 0
    for (plano, x, y, z), sala in por_celda.items():
        for direccion, (dx, dy) in VECINOS.items():
            vecina = por_celda.get((plano, x + dx, y + dy, z))
            if vecina and crear_salida(sala, direccion, vecina):
                automaticas += 1
    informar(f"Salidas automáticas de la grilla: |w{automaticas}|n")

    # --- 5. Anclas de los interiores --------------------------------------
    ancladas = 0
    for clave in ubicaciones.ANCLADAS:
        interior = salas[clave]
        for a, ida, b, vuelta in datos.CONEXIONES:
            if b == clave and ida is not None:
                interior.db.ancla = salas[a]
                ancladas += 1
                break
            if a == clave and vuelta is not None:
                interior.db.ancla = salas[b]
                ancladas += 1
                break
    informar(f"Interiores anclados a su calle: |w{ancladas}|n")

    inicio = salas[datos.SALA_INICIO]

    # --- 6. Salas de ejemplo de Evennia -----------------------------------
    ejemplos = []
    if borrar_ejemplos:
        for nombre in SALAS_EJEMPLO:
            for obj in search.search_object(nombre, exact=True):
                if obj not in por_celda.values() and obj.destination is None:
                    ejemplos.append(obj)

    condenadas = set(viejos) | set(ejemplos)

    # --- 7. Rescatar lo que esté parado sobre algo que va a desaparecer ---
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

    # --- 8. Recién ahora, borrar ------------------------------------------
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
        "relleno": relleno,
        "salidas": manuales + automaticas,
        "borradas": borradas,
        "inicio": inicio,
    }
