# -*- coding: utf-8 -*-
"""
Construye (y reconstruye) el mapa de pruebas desde `world.mapa.silent_hill`.

Uso desde el juego, como superusuario::

    batchcode batch.silent_hill

Uso desde la línea de comandos::

    docker compose exec game evennia shell -c "from world.mapa.constructor import construir; construir()"

Es idempotente: cada corrida borra lo que dejó la corrida anterior y levanta
todo de cero desde los datos. Solo toca objetos con la etiqueta del mapa, así
que lo que hayas creado a mano dentro de una sala se pierde junto con la sala,
pero nada de afuera del mapa se ve afectado.
"""

import os
from collections import defaultdict, deque

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from evennia.objects.models import ObjectDB
from evennia.objects.objects import DefaultExit, DefaultRoom
from evennia.utils import create, search

from world.mapa import silent_hill as datos

# Etiqueta que marca todo lo que pertenece al mapa generado. Es la que se usa
# para borrar antes de reconstruir.
TAG_MAPA = "silent_hill"
TAG_CATEGORIA = "mapa"

# Salas de ejemplo que Evennia crea de fábrica y que no queremos en el juego.
SALAS_EJEMPLO = ("Limbo",)

# Archivo que el constructor genera con los dbref resultantes. settings.py lo
# importa para saber dónde arranca el juego. Está en .gitignore porque los
# dbref son propios de cada base de datos.
ARCHIVO_GENERADO = os.path.join(
    settings.GAME_DIR, "server", "conf", "mapa_generado.py"
)


# --------------------------------------------------------------------------
# Validación de los datos
# --------------------------------------------------------------------------


def validar():
    """
    Revisa `silent_hill.py` antes de tocar la base de datos.

    Returns:
        list: mensajes de error. Vacía si los datos son consistentes.

    """
    errores = []
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

    # Salas a las que no llega ninguna conexión: casi siempre es un typo.
    for clave in datos.SALAS:
        if clave not in salidas:
            errores.append(f"la sala '{clave}' no tiene ninguna conexión")

    # Todo tiene que ser alcanzable caminando desde la sala de inicio.
    if datos.SALA_INICIO in datos.SALAS:
        vistas = {datos.SALA_INICIO}
        cola = deque([datos.SALA_INICIO])
        while cola:
            actual = cola.popleft()
            for destino in salidas[actual].values():
                if destino not in vistas:
                    vistas.add(destino)
                    cola.append(destino)
        for clave in sorted(set(datos.SALAS) - vistas):
            errores.append(f"la sala '{clave}' no es alcanzable desde SALA_INICIO")

    return errores


# --------------------------------------------------------------------------
# Construcción
# --------------------------------------------------------------------------


def _alias_de(nombre):
    """
    Parte "café|cafe|5to2" en ("café", ["cafe", "5to2"]).

    Si la clave es una dirección conocida, le suma los alias de DIRECCIONES.

    """
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


def construir(caller=None, borrar_ejemplos=True):
    """
    Borra el mapa anterior y lo reconstruye desde los datos.

    Args:
        caller (Object, optional): si viene, se le informan los pasos in-game.
        borrar_ejemplos (bool): además elimina las salas de ejemplo de Evennia
            (Limbo), una vez que hay a dónde mudar lo que estuviera adentro.

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
        informar("|rEl mapa tiene errores. No se construyó nada.|n")
        for err in errores:
            informar(f"  - {err}")
        return {"errores": errores}

    # --- 1. Lo que quedó de una corrida anterior, antes de crear nada nuevo.
    viejos = list(search.search_tag(TAG_MAPA, category=TAG_CATEGORIA))
    informar(f"Objetos del mapa anterior a reemplazar: |w{len(viejos)}|n")

    # --- 2. Salas.
    salas = {}
    for clave, spec in datos.SALAS.items():
        desc = spec["desc"]
        if spec.get("exterior"):
            desc = datos.NIEBLA + desc
        salas[clave] = create.create_object(
            settings.BASE_ROOM_TYPECLASS,
            key=spec["nombre"],
            attributes=[("desc", desc)],
            # Sin home: una sala no vive dentro de nada, y pedirlo obligaría a
            # resolver settings.DEFAULT_HOME, que en este punto todavía puede
            # estar apuntando a una sala que esta misma corrida va a borrar.
            nohome=True,
            tags=[
                (TAG_MAPA, TAG_CATEGORIA),
                (spec["distrito"], "distrito"),
                (clave, "clave_mapa"),
            ],
        )
    informar(f"Salas creadas: |w{len(salas)}|n")

    # --- 3. Salidas.
    total_salidas = 0
    for a, ida, b, vuelta in datos.CONEXIONES:
        for origen, nombre, destino in (
            (salas[a], ida, salas[b]),
            (salas[b], vuelta, salas[a]),
        ):
            if nombre is None:
                continue
            clave, alias = _alias_de(nombre)
            create.create_object(
                settings.BASE_EXIT_TYPECLASS,
                key=clave,
                aliases=alias,
                location=origen,
                destination=destino,
                nohome=True,
                tags=[(TAG_MAPA, TAG_CATEGORIA)],
            )
            total_salidas += 1
    informar(f"Salidas creadas: |w{total_salidas}|n")

    inicio = salas[datos.SALA_INICIO]

    # --- 4. Salas de ejemplo que trae Evennia.
    ejemplos = []
    if borrar_ejemplos:
        for nombre in SALAS_EJEMPLO:
            for obj in search.search_object(nombre, exact=True):
                if obj not in salas.values() and obj.destination is None:
                    ejemplos.append(obj)

    condenadas = set(viejos) | set(ejemplos)

    # --- 5. Rescatar lo que esté parado sobre algo que va a desaparecer.
    #        Alcanza con mirar todo lo que no sea sala ni salida: personajes
    #        (estén o no poseídos por una cuenta) y objetos sueltos.
    #        Ojo: location=None no es un huérfano. Es el estado normal de un
    #        personaje deslogueado, que Evennia saca del mundo hasta que su
    #        cuenta vuelva. A esos hay que corregirles el home y el lugar de
    #        reingreso, no meterlos al mapa a la fuerza.
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

    # --- 6. Recién ahora, borrar. Al borrar una sala se van con ella sus
    #        salidas, así que la mitad de esta lista ya no existe para cuando
    #        le llega el turno: eso no es un error.
    borradas = 0
    for obj in condenadas:
        try:
            obj.delete()
            borradas += 1
        except ObjectDoesNotExist:
            pass
    informar(f"Objetos borrados: |w{borradas}|n")
    if ejemplos:
        informar(
            "Salas de ejemplo eliminadas: |w"
            + ", ".join(o.key for o in ejemplos)
            + "|n"
        )

    # --- 7. Dejar el punto de partida donde settings.py lo pueda leer.
    _escribir_generado(inicio)
    informar(
        f"\nEl juego arranca en |c{inicio.key}|n (|w#{inicio.id}|n).\n"
        "|yPara que el server tome el nuevo punto de partida hay que "
        "reiniciarlo:|n\n"
        "    docker compose restart game"
    )

    return {
        "salas": len(salas),
        "salidas": total_salidas,
        "borradas": borradas,
        "inicio": inicio,
    }
