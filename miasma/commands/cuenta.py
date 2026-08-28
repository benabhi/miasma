# -*- coding: utf-8 -*-
"""
Comandos de cuenta (fuera de personaje), en español.

Mismas reglas que `commands/jugador.py`: el `key` va en español, los nombres
originales en inglés quedan como alias, y el docstring es la ayuda.

Tres comandos se traducen solo en nombre y ayuda, y su salida sigue saliendo en
inglés: `opciones`, `color` y `privado`. Son los tres más largos de Evennia
(177, 170 y 242 líneas) y copiar su `func()` para traducir un puñado de
mensajes deja mucho código que se desincroniza en cada actualización. Están
marcados con un aviso en su propia ayuda.
"""

from evennia.commands.default import account, comms
from evennia.utils import logger


class CmdSalir(account.CmdQuit):
    """
    desconectarte del juego

    Uso:
      salir

    Switch:
      all - cierra todas tus sesiones

    Cierra tu sesión actual de forma ordenada. Con /all cerrás todas.
    """

    key = "salir"
    aliases = ["quit"]
    help_category = "general"

    def func(self):
        cuenta = self.account

        if "all" in self.switches:
            cuenta.msg(
                "|RCerrando|n todas las sesiones. Ojalá vuelvas pronto.",
                session=self.session,
            )
            for sesion in cuenta.sessions.all():
                cuenta.disconnect_session_from_account(sesion, "quit/all")
            return

        abiertas = len(cuenta.sessions.all())
        if abiertas == 2:
            cuenta.msg("|RCerrando|n. Te queda una sesión abierta.", session=self.session)
        elif abiertas > 2:
            cuenta.msg(
                f"|RCerrando|n. Te quedan {abiertas - 1} sesiones abiertas.",
                session=self.session,
            )
        else:
            cuenta.msg("|RCerrando|n. Ojalá vuelvas pronto.", session=self.session)
        cuenta.disconnect_session_from_account(self.session, "quit")


class CmdEncarnar(account.CmdIC):
    """
    meterte en la piel de un personaje

    Uso:
      encarnar <personaje>

    Pasás a jugar como ese personaje. Sin argumento, volvés al último que
    hayas jugado.

    No podés encarnar a alguien que ya esté siendo jugado por otra cuenta.
    """

    key = "encarnar"
    aliases = ["ic", "puppet"]
    help_category = "general"

    def func(self):
        from evennia.utils import search, utils

        cuenta = self.account
        sesion = self.session
        candidatos = []

        if not self.args:
            candidatos = [cuenta.db._last_puppet] if cuenta.db._last_puppet else []
            if not candidatos:
                self.msg("Uso: encarnar <personaje>")
                return
        else:
            if jugables := cuenta.characters:
                candidatos.extend(
                    utils.make_iter(
                        cuenta.search(
                            self.args,
                            candidates=jugables,
                            search_object=True,
                            quiet=True,
                        )
                    )
                )
            # Los builders y superiores pueden encarnar más que sus personajes
            # jugables: primero se busca en la sala donde están, y solo si no
            # hay nada se cae a una búsqueda global.
            if cuenta.locks.check_lockstring(cuenta, "perm(Builder)"):
                if sesion.puppet:
                    candidatos = [
                        obj
                        for obj in sesion.puppet.search(self.args, quiet=True)
                        if obj.access(cuenta, "puppet")
                    ]
                if not candidatos:
                    candidatos.extend(
                        obj
                        for obj in search.object_search(self.args)
                        if obj.access(cuenta, "puppet")
                    )

        if not candidatos:
            self.msg("Ese personaje no existe, o no podés jugarlo.")
            return
        if len(candidatos) > 1:
            listado = ", ".join(f"{obj.key}(#{obj.id})" for obj in candidatos)
            self.msg(f"Hay varios con ese nombre:\n {listado}")
            return

        nuevo = candidatos[0]
        try:
            cuenta.puppet_object(sesion, nuevo)
            cuenta.db._last_puppet = nuevo
            logger.log_sec(
                f"Puppet Success: (Caller: {cuenta}, Target: {nuevo}, "
                f"IP: {self.session.address})."
            )
        except RuntimeError as exc:
            self.msg(f"|rNo podés encarnar a |C{nuevo.name}|n: {exc}")
            logger.log_sec(
                f"Puppet Failed: (Caller: {cuenta}, Target: {nuevo}, "
                f"IP: {self.session.address})."
            )


class CmdDesencarnar(account.CmdOOC):
    """
    salir del personaje

    Uso:
      desencarnar

    Dejás el personaje y volvés al limbo de la cuenta, sin cuerpo. Usá
    |wencarnar|n para volver al juego.
    """

    key = "desencarnar"
    aliases = ["ooc", "unpuppet"]
    help_category = "general"

    def func(self):
        cuenta = self.account
        sesion = self.session

        anterior = cuenta.get_puppet(sesion)
        if not anterior:
            self.msg("Ya estás fuera de personaje.")
            return

        cuenta.db._last_puppet = anterior
        try:
            cuenta.unpuppet_object(sesion)
            self.msg("\n|GSalís del personaje.|n\n")
            self.msg(cuenta.at_look(target=self.playable, session=sesion))
        except RuntimeError as exc:
            self.msg(f"|rNo se pudo salir de |c{anterior}|n: {exc}")


class CmdCrearPj(account.CmdCharCreate):
    """
    crear un personaje nuevo

    Uso:
      crearpj <nombre> [= descripción]

    Crea un personaje, con una descripción opcional. Podés usar mayúsculas en
    el nombre: igual vas a poder referirte a él en minúsculas.
    """

    key = "crearpj"
    aliases = ["crearpersonaje", "charcreate"]
    help_category = "general"

    def func(self):
        if not self.args:
            self.msg("Uso: crearpj <nombre> [= descripción]")
            return

        nuevo, errores = self.account.create_character(
            key=self.lhs,
            description=self.rhs or "Esto es un personaje.",
            ip=self.session.address,
        )
        if errores:
            self.msg(errores)
        if not nuevo:
            return
        self.msg(
            f"Se creó el personaje {nuevo.key}. Usá |wencarnar {nuevo.key}|n para "
            "entrar al juego con él."
        )


class CmdBorrarPj(account.CmdCharDelete):
    """
    borrar un personaje — esto no se puede deshacer

    Uso:
      borrarpj <nombre>

    Destruye para siempre uno de tus personajes.
    """

    key = "borrarpj"
    aliases = ["borrarpersonaje", "chardelete"]
    help_category = "general"

    def func(self):
        from evennia.utils import utils
        from evennia.utils.evmenu import get_input

        cuenta = self.account

        if not self.args:
            self.msg("Uso: borrarpj <nombre>")
            return

        coincidencias = [
            pj
            for pj in utils.make_iter(cuenta.characters)
            if pj.key.lower() == self.args.lower()
        ]
        if not coincidencias:
            self.msg("No tenés ningún personaje con ese nombre.")
            return
        if len(coincidencias) > 1:
            self.msg(
                "Cancelado: tenés dos personajes con el mismo nombre. Pedile a un "
                "administrador que borre el correcto."
            )
            return

        elegido = coincidencias[0]
        if not elegido.access(cuenta, "delete"):
            self.msg("No tenés permiso para borrar este personaje.")
            return

        cuenta.ndb._char_to_delete = elegido

        def _confirmar(caller, prompt, respuesta):
            if respuesta.lower() in ("si", "sí", "yes"):
                objetivo = caller.ndb._char_to_delete
                nombre = objetivo.key
                caller.characters.remove(objetivo)
                objetivo.delete()
                self.msg(f"El personaje '{nombre}' fue borrado para siempre.")
                logger.log_sec(
                    f"Character Deleted: {nombre} (Caller: {cuenta}, "
                    f"IP: {self.session.address})."
                )
            else:
                self.msg("Cancelado, no se borró nada.")
            del caller.ndb._char_to_delete

        get_input(
            cuenta,
            f"|rEsto destruye a '{elegido.key}' para siempre. No se puede deshacer.|n "
            "¿Seguir? si/[no]?",
            _confirmar,
        )


class CmdContrasena(account.CmdPassword):
    """
    cambiar tu contraseña

    Uso:
      contrasena <contraseña vieja> = <contraseña nueva>

    Elegí una segura.
    """

    key = "contrasena"
    aliases = ["contraseña", "password"]
    help_category = "general"

    def func(self):
        cuenta = self.account
        if not self.rhs:
            self.msg("Uso: contrasena <contraseña vieja> = <contraseña nueva>")
            return
        vieja, nueva = self.lhslist[0], self.rhslist[0]

        valida, error = cuenta.validate_password(nueva)

        if not cuenta.check_password(vieja):
            self.msg("La contraseña vieja no es correcta.")
        elif not valida:
            self.msg("\n".join(error.messages))
        else:
            cuenta.set_password(nueva)
            cuenta.save()
            self.msg("Contraseña cambiada.")
            logger.log_sec(
                f"Password Changed: {cuenta} (Caller: {cuenta}, IP: {self.session.address})."
            )


class CmdSesiones(account.CmdSessions):
    """
    ver tus sesiones conectadas

    Uso:
      sesiones

    Lista las sesiones abiertas contra tu cuenta.
    """

    key = "sesiones"
    aliases = ["sessions"]
    help_category = "general"

    def func(self):
        cuenta = self.account
        tabla = self.styled_table(
            "|wid", "|wprotocolo", "|worigen", "|wpersonaje", "|wlugar"
        )
        for sesion in sorted(cuenta.sessions.all(), key=lambda x: x.sessid):
            pj = cuenta.get_puppet(sesion)
            tabla.add_row(
                str(sesion.sessid),
                str(sesion.protocol_key),
                isinstance(sesion.address, tuple) and sesion.address[0] or sesion.address,
                pj and str(pj) or "ninguno",
                pj and str(pj.location) or "-",
            )
        self.msg(f"|wTus sesiones abiertas:|n\n{tabla}")


class CmdQuien(account.CmdWho):
    """
    ver quién está conectado

    Uso:
      quien

    Lista a todos los que están en el juego en este momento. El staff ve además
    datos de la sesión.
    """

    key = "quien"
    aliases = ["quién", "who", "doing"]
    help_category = "general"

    def func(self):
        import time

        import evennia
        from evennia.utils import utils

        cuenta = self.account
        sesiones = sorted(
            evennia.SESSION_HANDLER.get_sessions(), key=lambda o: o.account.key
        )
        # 'doing' es la variante pública: nunca muestra datos de sesión.
        detallado = self.cmdstring != "doing" and (
            cuenta.check_permstring("Developer") or cuenta.check_permstring("Admins")
        )

        if detallado:
            tabla = self.styled_table(
                "|wCuenta",
                "|wConectado",
                "|wInactivo",
                "|wPersonaje",
                "|wLugar",
                "|wCmds",
                "|wProtocolo",
                "|wOrigen",
            )
        else:
            tabla = self.styled_table("|wCuenta", "|wConectado", "|wInactivo")

        for sesion in sesiones:
            if not sesion.logged_in:
                continue
            inactivo = time.time() - sesion.cmd_last_visible
            conectado = time.time() - sesion.conn_time
            suya = sesion.get_account()
            fila = [
                utils.crop(suya.get_display_name(cuenta), width=25),
                utils.time_format(conectado, 0),
                utils.time_format(inactivo, 1),
            ]
            if detallado:
                pj = sesion.get_puppet()
                fila += [
                    utils.crop(pj.get_display_name(cuenta) if pj else "ninguno", width=25),
                    utils.crop(pj.location.key if pj and pj.location else "-", width=25),
                    sesion.cmd_total,
                    sesion.protocol_key,
                    isinstance(sesion.address, tuple) and sesion.address[0] or sesion.address,
                ]
            tabla.add_row(*fila)

        total = evennia.SESSION_HANDLER.account_count()
        pie = (
            "Hay una cuenta conectada."
            if total == 1
            else f"Hay {total} cuentas conectadas."
        )
        self.msg(f"|wConectados:|n\n{tabla}\n{pie}")


class CmdAtenuar(account.CmdQuell):
    """
    usar los permisos del personaje en vez de los de la cuenta

    Uso:
      atenuar
      desatenuar

    Normalmente manda el nivel de permiso de la cuenta. Este comando hace que
    valga el del personaje que estés jugando, que es útil para probar cómo ve
    el juego alguien con menos permisos. Solo funciona hacia abajo: no podés
    escalar permisos encarnando a alguien con más.
    """

    key = "atenuar"
    aliases = ["desatenuar", "quell", "unquell"]
    help_category = "general"


class CmdEstilo(account.CmdStyle):
    """
    ver y cambiar las opciones de estilo de tu cuenta

    Uso:
      estilo
      estilo <opción> = <valor>
    """

    key = "estilo"
    aliases = ["style"]
    help_category = "general"


class CmdOpciones(account.CmdOption):
    """
    ver y cambiar las opciones de tu cliente

    Uso:
      opciones[/save] [nombre = valor]

    |yNota: la salida de este comando todavía sale en inglés.|n
    """

    key = "opciones"
    aliases = ["option", "options"]
    help_category = "general"


class CmdColor(account.CmdColorTest):
    """
    ver los colores que soporta tu cliente

    Uso:
      color ansi || xterm256

    |yNota: la salida de este comando todavía sale en inglés.|n
    """

    key = "color"
    help_category = "general"


class CmdPrivado(comms.CmdPage):
    """
    mandarle un mensaje privado a alguien

    Uso:
      privado <alguien> = <mensaje>
      privado <mensaje>

    Sin destinatario, le responde al último con el que hablaste.

    |yNota: la salida de este comando todavía sale en inglés.|n
    """

    key = "privado"
    aliases = ["mp", "page", "tell"]
    help_category = "comunicación"


class CmdMirarOOC(account.CmdOOCLook):
    """
    mirar estando fuera de personaje

    Uso:
      mirar

    Muestra la pantalla de la cuenta: tus sesiones abiertas y tus personajes.

    Es un comando distinto del |wmirar|n de dentro del juego. Fuera de personaje
    no hay dónde estar parado, así que no hay sala que mirar: lo que se mira es
    la cuenta.
    """

    key = "mirar"
    aliases = ["m", "ver", "look", "l", "ls"]
    help_category = "general"
