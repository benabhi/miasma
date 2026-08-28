# -*- coding: utf-8 -*-
"""
Salas.

Toda sala de Miasma lleva un lugar en el mapa. Esa es la diferencia con la sala
por defecto de Evennia: acá `tipo_mapa` no es opcional, porque el minimapa se
dibuja en cada `mirar` y una sala sin icono deja un agujero visible.

Los datos del mapa viven en Attributes, no en atributos de clase, porque los
escribe el constructor del mundo y tienen que sobrevivir a un reload:

    tipo_mapa (str)   qué se dibuja: "calle", "comercio", "iglesia"…
                      (el catálogo está en world/mapa/iconos.py)
    plano (str)       a qué mapa pertenece: "pueblo", "escuela", "hospital"…
    pos (tuple)       (x, y, z) dentro del plano. x al este, y al norte,
                      z el piso.
    ancla (Room)      solo para interiores de una sala, que no tienen celda
                      propia: la sala de la que se entra, que es la que se
                      dibuja en el minimapa.

Una sala tiene `pos` o tiene `ancla`, nunca las dos.
"""

from evennia.objects.objects import DefaultRoom
from evennia.utils import ansi
from evennia.utils.evtable import EvTable

from world.mapa import render

from .objects import ObjectParent

# Ancho reservado para la columna de la descripción cuando no se puede saber el
# del cliente.
ANCHO_POR_DEFECTO = 78

# La paleta del texto de sala, la misma de la pantalla de conexión: rojo
# apagado para el nombre del lugar, gris oscuro para las etiquetas del pie. La
# descripción va sin color, que es lo único que se lee largo.
TITULO = "|R"          # el nombre de la sala
ETIQUETA = "|x"        # "Salidas:", "Personajes:", "Ves:"
LISTA = "|w"           # lo que viene después de la etiqueta

# Celdas a cada lado del centro en el minimapa de `mirar`. Con 3 entra una
# manzana entera con sus calles alrededor, que es lo mínimo para orientarse en
# una retícula con calle cada tres celdas. Más que eso le come ancho a la
# descripción; para ver todo está el comando `mapa`.
RADIO_MINIMAPA = 3


class Room(ObjectParent, DefaultRoom):
    """
    Sala del mundo, con su lugar en el mapa.
    """

    # Fallback si nadie definió el tipo. Se dibuja como "?" para que se note.
    tipo_mapa_por_defecto = "interior"

    def at_object_creation(self):
        super().at_object_creation()
        if not self.db.tipo_mapa:
            self.db.tipo_mapa = self.tipo_mapa_por_defecto

    # ----------------------------------------------------------------------
    # Apariencia: minimapa a la izquierda, texto a la derecha
    # ----------------------------------------------------------------------

    def return_appearance(self, looker, **kwargs):
        """
        Arma la vista de la sala en dos columnas y un pie.

        Arriba, el minimapa al lado del nombre y la descripción. Abajo, a todo
        el ancho, las salidas, los personajes y las cosas: esas listas crecen y
        encajonarlas en una columna angosta las vuelve ilegibles.

        """
        if not looker:
            return ""

        ancho = self._ancho_de(looker)
        mapa, _tipos = render.dibujar(self, radio=RADIO_MINIMAPA, recortar=False)

        nombre = self.get_display_name(looker, **kwargs)
        desc = self.get_display_desc(looker, **kwargs)
        texto = f"|c{nombre}|n\n\n{desc}" if desc else f"|c{nombre}|n"

        if mapa:
            ancho_mapa = max(len(ansi.strip_ansi(l)) for l in mapa)
            # 3 de separación entre columnas; el resto para el texto.
            ancho_texto = max(30, ancho - ancho_mapa - 3)
            tabla = EvTable(
                border=None,
                pad_left=0,
                pad_right=0,
                table=[["\n".join(mapa)], [texto]],
            )
            tabla.reformat_column(0, width=ancho_mapa + 3, valign="t")
            tabla.reformat_column(1, width=ancho_texto, valign="t")
            arriba = str(tabla)
        else:
            arriba = texto

        pie = [
            bloque
            for bloque in (
                self.get_display_exits(looker, **kwargs),
                self.get_display_characters(looker, **kwargs),
                self.get_display_things(looker, **kwargs),
            )
            if bloque
        ]

        partes = [arriba]
        if pie:
            partes.append("\n".join(pie))
        return "\n".join(partes)

    @staticmethod
    def _ancho_de(looker):
        """Ancho útil del cliente de quien está mirando."""
        sesiones = getattr(looker, "sessions", None)
        if sesiones:
            for sesion in sesiones.all():
                ancho = sesion.protocol_flags.get("SCREENWIDTH", {}).get(0)
                if ancho:
                    return min(int(ancho), 100)
        return ANCHO_POR_DEFECTO

    # ----------------------------------------------------------------------
    # El pie, en la paleta del juego
    #
    # Evennia los devuelve con la etiqueta en blanco fuerte, que compite con la
    # descripción. Acá la etiqueta va en gris oscuro y la lista en blanco: se
    # lee primero el texto y después dónde se puede ir.
    # ----------------------------------------------------------------------

    def get_display_exits(self, looker, **kwargs):
        original = super().get_display_exits(looker, **kwargs)
        return self._recolorear(original)

    def get_display_characters(self, looker, **kwargs):
        original = super().get_display_characters(looker, **kwargs)
        return self._recolorear(original)

    def get_display_things(self, looker, **kwargs):
        original = super().get_display_things(looker, **kwargs)
        return self._recolorear(original)

    @staticmethod
    def _recolorear(bloque):
        """
        Cambia la paleta de un bloque del pie sin rehacer cómo se arma.

        Evennia devuelve `|wEtiqueta:|n lista`. Reescribir los tres métodos
        enteros para cambiarles dos códigos de color sería copiar la lógica de
        ordenar, agrupar y pluralizar solo para pintarla distinto.

        """
        if not bloque:
            return bloque
        return bloque.replace("|w", ETIQUETA, 1).replace("|n ", f"|n {LISTA}", 1) + "|n"
