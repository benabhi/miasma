# -*- coding: utf-8 -*-
"""
Comandos de personaje, en español.

Cada clase hereda del comando equivalente de Evennia y cambia:

- `key`: el nombre en español, que es el que se muestra en la ayuda.
- `aliases`: incluyen **siempre** el nombre y los alias originales en inglés,
  para que los ejemplos de la documentación de Evennia sigan funcionando.
- el docstring: en Evennia el docstring *es* la entrada de ayuda.
- los strings de `func()` que estaban hardcodeados en inglés.

Cuando hay que reescribir `func()` entero se copia la lógica del original. Eso
implica que un cambio de comportamiento upstream no llega solo: al actualizar
Evennia hay que revisar los `func()` copiados. Los comandos que solo cambian
nombre y ayuda no tienen ese problema.

Los mensajes que no salen de acá sino del motor (la descripción de la sala, las
salidas, los mensajes de movimiento) se traducen por el catálogo gettext en
`locale/es/LC_MESSAGES/django.po`, no acá.
"""

from evennia.commands.default import general, help
from evennia.utils import utils

from commands.command import Command
from world.mapa import iconos, render, ubicaciones


class CmdMirar(general.CmdLook):
    """
    mirar el lugar o un objeto

    Uso:
      mirar
      mirar <objeto>
      mirar *<cuenta>

    Observa el lugar donde estás o algo que tengas cerca.
    """

    key = "mirar"
    aliases = ["m", "ver", "look", "l", "ls"]
    help_category = "general"

    def func(self):
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("No estás en ningún lado, no hay nada que mirar.")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        self.msg(text=(caller.at_look(target), {"type": "look"}), options=None)


class CmdInventario(general.CmdInventory):
    """
    ver lo que llevás encima

    Uso:
      inventario
      inv

    Muestra todo lo que estás cargando.
    """

    key = "inventario"
    aliases = ["inv", "i", "inventory"]
    help_category = "general"

    def func(self):
        items = self.caller.contents
        if not items:
            texto = "No llevás nada encima."
        else:
            from evennia.utils.ansi import raw as raw_ansi

            tabla = self.styled_table(border="header")
            for clave, desc, _ in utils.group_objects_by_key_and_desc(
                items, caller=self.caller
            ):
                tabla.add_row(
                    f"|C{clave}|n",
                    "{}|n".format(utils.crop(raw_ansi(desc or ""), width=50) or ""),
                )
            texto = f"|wLlevás encima:\n{tabla}"
        self.msg(text=(texto, {"type": "inventory"}))


class CmdTomar(general.CmdGet):
    """
    levantar algo del suelo

    Uso:
      tomar <objeto>

    Levanta algo del lugar donde estás y lo pasa a tu inventario.
    """

    key = "tomar"
    aliases = ["agarrar", "get", "grab"]
    help_category = "general"

    def func(self):
        caller = self.caller

        if not self.args:
            self.msg("¿Tomar qué?")
            return
        objs = caller.search(self.args, location=caller.location, stacked=self.number)
        if not objs:
            return
        objs = utils.make_iter(objs)

        if len(objs) == 1 and caller == objs[0]:
            self.msg("No podés tomarte a vos mismo.")
            return

        for obj in objs:
            if not obj.access(caller, "get"):
                self.msg(obj.db.get_err_msg or "No podés tomar eso.")
                return
            if not obj.at_pre_get(caller):
                return

        movidos = []
        for obj in objs:
            if obj.move_to(caller, quiet=True, move_type="get"):
                movidos.append(obj)
                obj.at_get(caller)

        if not movidos:
            self.msg("Eso no se puede levantar.")
            return

        nombre = movidos[0].get_numbered_name(len(movidos), caller, return_string=True)
        caller.msg(f"Levantás {nombre}.")
        caller.location.msg_contents(
            "{quien} levanta " + nombre + ".",
            mapping={"quien": caller},
            exclude=caller,
            from_obj=caller,
        )


class CmdSoltar(general.CmdDrop):
    """
    soltar algo que llevás

    Uso:
      soltar <objeto>

    Deja un objeto de tu inventario en el lugar donde estás.
    """

    key = "soltar"
    aliases = ["tirar", "drop"]
    help_category = "general"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("¿Soltar qué?")
            return

        objs = caller.search(
            self.args,
            location=caller,
            nofound_string=f"No estás llevando {self.args}.",
            multimatch_string=f"Llevás más de un {self.args}:",
            stacked=self.number,
        )
        if not objs:
            return
        objs = utils.make_iter(objs)

        for obj in objs:
            if not obj.at_pre_drop(caller):
                return

        movidos = []
        for obj in objs:
            if obj.move_to(caller.location, quiet=True, move_type="drop"):
                movidos.append(obj)
                obj.at_drop(caller)

        if not movidos:
            self.msg("Eso no se puede soltar.")
            return

        nombre = movidos[0].get_numbered_name(len(movidos), caller, return_string=True)
        caller.msg(f"Soltás {nombre}.")
        caller.location.msg_contents(
            "{quien} suelta " + nombre + ".",
            mapping={"quien": caller},
            exclude=caller,
            from_obj=caller,
        )


class CmdDar(general.CmdGive):
    """
    darle algo a alguien

    Uso:
      dar <objeto> a <alguien>
      dar <objeto> = <alguien>

    Pasa algo de tu inventario al inventario de otra persona.
    """

    key = "dar"
    aliases = ["give"]
    help_category = "general"
    rhs_split = ("=", " a ", " to ")

    def func(self):
        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Uso: dar <objeto> a <alguien>")
            return

        a_dar = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"No estás llevando {self.lhs}.",
            multimatch_string=f"Llevás más de un {self.lhs}:",
            stacked=self.number,
        )
        if not a_dar:
            return
        destino = caller.search(self.rhs)
        if not destino:
            return

        a_dar = utils.make_iter(a_dar)
        singular, plural = a_dar[0].get_numbered_name(len(a_dar), caller)
        if destino == caller:
            caller.msg(f"Te quedás con {plural if len(a_dar) > 1 else singular}.")
            return

        for obj in a_dar:
            if not obj.at_pre_give(caller, destino):
                return

        movidos = []
        for obj in a_dar:
            if obj.move_to(destino, quiet=True, move_type="give"):
                movidos.append(obj)
                obj.at_give(caller, destino)

        if not movidos:
            caller.msg(f"No pudiste darle eso a {destino.get_display_name(caller)}.")
            return

        nombre = a_dar[0].get_numbered_name(len(movidos), caller, return_string=True)
        caller.msg(f"Le das {nombre} a {destino.get_display_name(caller)}.")
        destino.msg(f"{caller.get_display_name(destino)} te da {nombre}.")


class CmdDescribirme(general.CmdSetDesc):
    """
    escribir tu propia descripción

    Uso:
      describirme <descripción>

    Define cómo te ven los demás cuando te miran.
    """

    key = "describirme"
    aliases = ["descripcion", "descripción", "setdesc"]
    help_category = "general"

    def func(self):
        if not self.args:
            self.msg("Tenés que escribir una descripción.")
            return
        self.caller.db.desc = self.args.strip()
        self.msg("Listo, esa es tu descripción.")


class CmdDecir(general.CmdSay):
    """
    hablar en voz alta

    Uso:
      decir <mensaje>
      "<mensaje>

    Te escucha todo el que esté en el mismo lugar que vos.
    """

    key = "decir"
    aliases = ['"', "'", "say", "hablar"]
    help_category = "general"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("¿Decir qué?")
            return
        habla = caller.at_pre_say(self.args)
        if not habla:
            return
        caller.at_say(habla, msg_self=True)


class CmdSusurrar(general.CmdWhisper):
    """
    hablarle al oído a alguien

    Uso:
      susurrar <personaje> = <mensaje>
      susurrar <uno>, <otro> = <mensaje>

    Le hablás en privado a una o más personas que estén en el mismo lugar. Los
    demás no se enteran de lo que dijiste.
    """

    key = "susurrar"
    aliases = ["whisper"]
    help_category = "general"

    def func(self):
        caller = self.caller
        if not self.lhs or not self.rhs:
            caller.msg("Uso: susurrar <personaje> = <mensaje>")
            return

        destinos = [d.strip() for d in self.lhs.split(",")]
        destinos = [caller.search(d) for d in set(destinos)]
        destinos = [d for d in destinos if d]

        habla = self.rhs
        if not habla or not destinos:
            return

        habla = caller.at_pre_say(habla, whisper=True, receivers=destinos)
        msg_self = None if caller in destinos else True
        caller.at_say(habla, msg_self=msg_self, receivers=destinos, whisper=True)


class CmdGesto(general.CmdPose):
    """
    hacer algo sin hablar

    Uso:
      gesto <texto>
      :<texto>

    Ejemplo:
      gesto se apoya contra la pared, sonriendo.
       -> los demás ven:
      Tomás se apoya contra la pared, sonriendo.

    Describe una acción. El texto arranca siempre con tu nombre.
    """

    key = "gesto"
    aliases = [":", "emote", "pose"]
    help_category = "general"

    def func(self):
        if not self.args:
            self.msg("¿Qué querés hacer?")
            return
        texto = f"{self.caller.name}{self.args}"
        self.caller.location.msg_contents(
            text=(texto, {"type": "pose"}), from_obj=self.caller
        )


class CmdCasa(general.CmdHome):
    """
    volver a tu punto de origen

    Uso:
      casa

    Te teletransporta al lugar que tengas fijado como hogar.
    """

    key = "casa"
    aliases = ["home"]
    help_category = "general"

    def func(self):
        caller = self.caller
        hogar = caller.home
        if not hogar:
            caller.msg("No tenés ningún lugar al que volver.")
        elif hogar == caller.location:
            caller.msg("Ya estás ahí.")
        else:
            caller.msg("Como en casa, en ningún lado ...")
            caller.move_to(hogar, move_type="teleport")


class CmdApodo(general.CmdNick):
    """
    definir tus propios atajos de escritura

    Uso:
      apodo[/switches] <cadena> [= [reemplazo]]
      apodo[/switches] <plantilla> = <plantilla de reemplazo>
      apodo/borrar <cadena> o /borrar <número>
      apodos

    Switches:
      entrada    - reemplaza lo que escribís (inputline, por defecto)
      objeto     - reemplaza nombres de objeto
      cuenta     - reemplaza nombres de cuenta
      lista      - muestra todos tus apodos
      borrar     - borra un apodo por nombre o número
      todo       - borra todos tus apodos

    Un apodo es un atajo tuyo: solo lo ves y lo usás vos.

    |yNota: la salida de este comando todavía sale en inglés.|n
    """

    key = "apodo"
    aliases = ["apodos", "nick", "nickname", "nicks"]
    help_category = "general"


class CmdAyuda(help.CmdHelp):
    """
    ayuda del juego

    Uso:
      ayuda
      ayuda <tema>
      ayuda <tema>/<subtema>

    Sin argumentos muestra el índice: todos los comandos que podés usar,
    agrupados por categoría. Con un tema, muestra su entrada.
    """

    key = "ayuda"
    aliases = ["?", "help"]
    help_category = "general"

    # El índice y las entradas se arman en métodos largos de Evennia (117 y 77
    # líneas). En vez de copiarlos —y quedar desincronizados en cada
    # actualización— se posprocesa lo que devuelven. Las etiquetas del índice
    # están rellenadas con guiones hasta el ancho del cliente, así que sus
    # reemplazos tienen exactamente la misma cantidad de caracteres para no
    # correr la línea: "Commands"/"Comandos" (8) y "Game & World"/"Ambientación"
    # (12).
    _REEMPLAZOS = (
        ("-Commands-", "-Comandos-"),
        ("-Game & World-", "-Ambientación-"),
        ("|CHelp for |w", "|CAyuda de |w"),
        ("|rNo help found|n", "|rNo hay ayuda|n"),
        ("|C(aliases: ", "|C(alias: "),
        ("|CSubtopics:|n", "|CSubtemas:|n"),
        ("|COther topic suggestions:|n", "|COtros temas parecidos:|n"),
        ("There is no help topic matching '", "No hay ninguna entrada de ayuda para '"),
        ("No help entry found for '", "No se encontró ayuda para '"),
    )

    @classmethod
    def _traducir(cls, texto):
        for ingles, espanol in cls._REEMPLAZOS:
            texto = texto.replace(ingles, espanol)
        return texto

    def format_help_entry(self, *args, **kwargs):
        return self._traducir(super().format_help_entry(*args, **kwargs))

    def format_help_index(self, *args, **kwargs):
        return self._traducir(super().format_help_index(*args, **kwargs))


class CmdMapa(Command):
    """
    ver el mapa de la zona

    Uso:
      mapa
      mapa <radio>

    Muestra el mapa completo del plano donde estás —el pueblo, la escuela, el
    hospital, las alcantarillas o el parque— con tu posición marcada, más una
    referencia de qué es cada símbolo.

    El minimapa de |wmirar|n muestra solo lo que tenés al lado. Este muestra
    todo lo que da la pantalla. Con un número, se ajusta cuánto abarca:

      mapa 5     - cinco celdas a cada lado
    """

    key = "mapa"
    aliases = ["map"]
    locks = "cmd:all()"
    help_category = "general"

    def func(self):
        sala = self.caller.location
        if not sala:
            self.msg("No estás en ningún lado.")
            return

        radio = 12
        if self.args.strip():
            if not self.args.strip().isdigit():
                self.msg("Uso: mapa [radio]")
                return
            radio = max(1, min(int(self.args.strip()), 30))

        lineas, tipos = render.dibujar(sala, radio=radio)
        if not lineas:
            self.msg("Acá no hay mapa. No todas las zonas están relevadas.")
            return

        centro = sala if render.posicion(sala) else render.ancla_de(sala)
        plano, _x, _y, z = render.posicion(centro)
        titulo = ubicaciones.NOMBRES_PLANO.get(plano, plano)

        cabecera = f"|c{titulo}|n"
        niveles = render.niveles_del_plano(plano)
        if len(niveles) > 1:
            cabecera += f" |x— nivel {z} de {min(niveles)}..{max(niveles)}|n"
        if centro is not sala:
            cabecera += f"\n|xEstás dentro de {sala.get_display_name(self.caller)}.|n"

        salida = [cabecera, ""] + lineas
        referencia = iconos.leyenda(tipos)
        if referencia:
            salida += ["", "|wReferencia:|n"] + referencia
        self.msg("\n".join(salida))
