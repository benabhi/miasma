# -*- coding: utf-8 -*-
"""
Conjuntos de comandos (cmdsets).

Cada cmdset arranca de la versión por defecto de Evennia y después reemplaza
los comandos de jugador por sus equivalentes en español.

**El `remove()` no es opcional.** Nuestros comandos llevan el nombre original en
inglés como alias; si el comando original siguiera en el cmdset, Evennia vería
dos candidatos para `look` y respondería con un multimatch en vez de ejecutar.
`CmdSet.remove()` acepta el key como string, así que no hace falta importar la
clase original solo para sacarla.

Los comandos de construcción y administración (los que empiezan con `@`, más
`ban`, `boot`, `emit`, `perm`, `wall`…) quedan en inglés a propósito: los usa el
staff y así se mantienen alineados con la documentación de Evennia.
"""

from evennia import default_cmds

from commands import cuenta, jugador, sin_loguear


def _reemplazar(cmdset, originales, nuevos):
    """
    Saca los comandos `originales` (por key) y agrega los `nuevos`.

    Args:
        cmdset (CmdSet): el cmdset que se está poblando.
        originales (iterable): keys de los comandos de Evennia a quitar.
        nuevos (iterable): clases de comando a agregar en su lugar.

    """
    for key in originales:
        cmdset.remove(key)
    for cmd in nuevos:
        cmdset.add(cmd)


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    Comandos disponibles sobre el personaje una vez dentro del juego.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        _reemplazar(
            self,
            (
                "look",
                "inventory",
                "get",
                "drop",
                "give",
                "setdesc",
                "say",
                "whisper",
                "pose",
                "home",
                "nick",
                "help",
            ),
            (
                jugador.CmdMirar,
                jugador.CmdInventario,
                jugador.CmdTomar,
                jugador.CmdSoltar,
                jugador.CmdDar,
                jugador.CmdDescribirme,
                jugador.CmdDecir,
                jugador.CmdSusurrar,
                jugador.CmdGesto,
                jugador.CmdCasa,
                jugador.CmdApodo,
                jugador.CmdAyuda,
                jugador.CmdMapa,
            ),
        )


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    Comandos de la cuenta. Se combinan con los del personaje al encarnarlo.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        _reemplazar(
            self,
            (
                "quit",
                "ic",
                "ooc",
                "charcreate",
                "chardelete",
                "password",
                "who",
                "quell",
                "style",
                "option",
                "color",
                "page",
                "nick",
                "look",
                "help",
            ),
            (
                cuenta.CmdSalir,
                cuenta.CmdEncarnar,
                cuenta.CmdDesencarnar,
                cuenta.CmdCrearPj,
                cuenta.CmdBorrarPj,
                cuenta.CmdContrasena,
                cuenta.CmdQuien,
                cuenta.CmdAtenuar,
                cuenta.CmdEstilo,
                cuenta.CmdOpciones,
                cuenta.CmdColor,
                cuenta.CmdPrivado,
                jugador.CmdApodo,
                cuenta.CmdMirarOOC,
                jugador.CmdAyuda,
            ),
        )


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Lo único disponible antes de identificarse.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        _reemplazar(
            self,
            ("connect", "create", "quit", "help", "encoding", "screenreader"),
            (
                sin_loguear.CmdConectar,
                sin_loguear.CmdCrear,
                sin_loguear.CmdSalir,
                sin_loguear.CmdAyuda,
                sin_loguear.CmdCodificacion,
                sin_loguear.CmdLector,
            ),
        )
        # El comando de sistema que muestra la pantalla de conexión conserva su
        # key (lo dispara el servidor), así que se reemplaza por su propia
        # subclase para sumarle los alias en español.
        self.add(sin_loguear.CmdMirarSinLoguear)


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    Comandos por sesión, disponibles siempre.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        _reemplazar(self, ("sessions",), (cuenta.CmdSesiones,))
