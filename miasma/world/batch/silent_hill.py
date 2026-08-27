# -*- coding: utf-8 -*-
"""
Batchcode: construye el mapa de pruebas de Silent Hill.

Desde el juego, como superusuario::

    batchcode batch.silent_hill

(El prefijo `world.` no va: `BASE_BATCHPROCESS_PATHS` ya incluye "world".)

Toda la lógica vive en `world.mapa.constructor`, para que se pueda invocar
también desde `evennia shell`. Este archivo es solo el punto de entrada del
procesador de batch.
"""

#HEADER

from world.mapa.constructor import construir

#CODE

construir(caller)  # noqa: F821  -- `caller` lo inyecta el batchprocessor
