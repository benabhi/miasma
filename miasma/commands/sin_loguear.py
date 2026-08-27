# -*- coding: utf-8 -*-
"""
Comandos disponibles antes de identificarse, en español.

Es lo primero que ve alguien que se conecta, así que acá no puede quedar nada
en inglés. Los mensajes de error de credenciales (usuario incorrecto, demasiados
intentos, baneado) no salen de estos comandos sino del motor, y ya vienen
traducidos por el catálogo gettext.

`conectar` y `crear` conservan la lógica original de Evennia: toda la validación
de contraseñas, el throttle anti-fuerza-bruta y el registro de seguridad viven
en `AccountDB.authenticate()` y `create_account()`, no en el comando.
"""

from django.conf import settings

from evennia.commands.default import unloggedin


class CmdConectar(unloggedin.CmdUnconnectedConnect):
    """
    entrar con una cuenta que ya tenés

    Uso:
      conectar <usuario> <contraseña>

    Si tu usuario tiene espacios, ponelo entre comillas:
      conectar "Ana la Roja" miContrasena123
    """

    key = "conectar"
    aliases = ["conectarse", "connect", "conn", "con", "co"]
    help_category = "general"


class CmdCrear(unloggedin.CmdUnconnectedCreate):
    """
    crear una cuenta nueva

    Uso:
      crear <usuario> <contraseña>

    Si tu usuario tiene espacios, ponelo entre comillas:
      crear "Ana la Roja" miContrasena123

    La cuenta no es el personaje: una vez adentro vas a crear tu sobreviviente
    aparte, con |wcrearpj|n.
    """

    key = "crear"
    aliases = ["create", "cr", "cre"]
    help_category = "general"


class CmdSalir(unloggedin.CmdUnconnectedQuit):
    """
    cortar la conexión

    Uso:
      salir
    """

    key = "salir"
    aliases = ["quit", "q", "qu"]
    help_category = "general"

    def func(self):
        sesion = self.caller
        sesion.sessionhandler.disconnect(sesion, "Hasta luego. Cerrando la conexión.")


class CmdAyuda(unloggedin.CmdUnconnectedHelp):
    """
    ayuda para el que todavía no entró

    Uso:
      ayuda
    """

    key = "ayuda"
    aliases = ["help", "h", "?"]
    help_category = "general"

    def func(self):
        texto = """
Todavía no entraste al juego. Desde acá podés:

  |wcrear|n        - crear una cuenta nueva
  |wconectar|n     - entrar con una cuenta que ya tengas
  |wmirar|n        - volver a mostrar la pantalla de conexión
  |wayuda|n        - mostrar esta ayuda
  |wcodificacion|n - cambiar la codificación de texto para tu cliente
  |wlector|n       - modo lector de pantalla
  |wsalir|n        - cortar la conexión

Primero creá una cuenta, por ejemplo: |wcrear Ana c67jHL8p|n
Si tu usuario tiene espacios, usá comillas: |wcrear "Ana la Roja" c67jHL8p|n
Después entrá al juego: |wconectar Ana c67jHL8p|n
"""
        if settings.STAFF_CONTACT_EMAIL:
            texto += f"\nPara soporte, escribí a: {settings.STAFF_CONTACT_EMAIL}\n"
        self.msg(texto)


class CmdMirarSinLoguear(unloggedin.CmdUnconnectedLook):
    """
    volver a mostrar la pantalla de conexión

    Uso:
      mirar
    """

    # El key es el comando de sistema que dispara el servidor al conectarse
    # (CMD_LOGINSTART): no se toca. Lo que se traduce son sus alias.
    aliases = ["mirar", "m", "ver", "look", "l"]
    help_category = "general"


class CmdCodificacion(unloggedin.CmdUnconnectedEncoding):
    """
    cambiar la codificación de texto

    Uso:
      codificacion
      codificacion <codificación>
      codificacion clear

    Sirve si ves caracteres raros en vez de acentos y eñes. Sin argumento,
    muestra la que está usando tu sesión.

    |yNota: la salida de este comando todavía sale en inglés.|n
    """

    key = "codificacion"
    aliases = ["codificación", "encoding", "encode"]
    help_category = "general"


class CmdLector(unloggedin.CmdUnconnectedScreenreader):
    """
    modo lector de pantalla

    Uso:
      lector

    Prende y apaga el modo pensado para lectores de pantalla. Una vez adentro
    del juego, se maneja con |wopciones screenreader on|n.
    """

    key = "lector"
    aliases = ["screenreader"]
    help_category = "general"

    def func(self):
        nuevo = not self.session.protocol_flags.get("SCREENREADER", False)
        self.session.protocol_flags["SCREENREADER"] = nuevo
        self.msg(
            "Modo lector de pantalla |w{}|n.".format("activado" if nuevo else "desactivado")
        )
        self.session.sessionhandler.session_portal_sync(self.session)
