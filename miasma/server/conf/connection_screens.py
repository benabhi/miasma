# -*- coding: utf-8 -*-
"""
Pantalla de conexión.

Es lo primero que ve alguien que se conecta, antes de identificarse. Define acá
una función `connection_screen()` sin argumentos para una pantalla dinámica, o
una variable de módulo con el texto. Si hay varias variables, Evennia elige una
al azar.

Los comandos disponibles en esta pantalla están en
evennia.default_cmds.UnloggedinCmdSet.
"""

from django.conf import settings

CONNECTION_SCREEN = """
|x·······················································|n
|R           M I A S M A|n
|x           {slogan}|n
|x·······················································|n

 El Brote fue hace semanas. La radio dejó de mentir hace días.
 Lo que respirás cambia a la gente, y no siempre en muertos.

 Si ya tenés cuenta:
      |wconectar <usuario> <contraseña>|n
 Si es tu primera vez:
      |wcrear <usuario> <contraseña>|n

 Si tu usuario tiene espacios, ponelo entre comillas.
 |wayuda|n para más info. |wmirar|n vuelve a mostrar esta pantalla.

|x·······················································|n
|x Sin héroes. Sin puntos de guardado. Solo lo que puedas cargar.|n
""".format(
    slogan=settings.GAME_SLOGAN
)
