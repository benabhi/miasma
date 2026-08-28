# -*- coding: utf-8 -*-
r"""
Configuración de MIASMA.

Solo se sobrescriben aquí los valores que realmente queremos distintos de los
defaults de Evennia. Todo lo demás vive en:

    https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Rutas de sistema de archivos: usar GAME_DIR y EVENNIA_DIR.
Rutas de Python del juego: relativas a la raíz del gamedir (ej. "typeclasses.foo").
Rutas de Python de la librería: explícitas (ej. "evennia.foo").

Los valores sensibles o propios de cada máquina (SECRET_KEY, DEBUG, credenciales
de base de datos) van en server/conf/secret_settings.py, que está en .gitignore.
"""

import os

# Usar los defaults de Evennia salvo lo que se sobrescriba explícitamente
from evennia.settings_default import *

######################################################################
# Identidad del juego
######################################################################

SERVERNAME = "Miasma"
GAME_SLOGAN = "El aire está enfermo. Vos también, todavía no lo sabés."

######################################################################
# Idioma y tiempo real
######################################################################

# Evennia trae traducción al español en evennia/locale/es. Activarla traduce
# los mensajes del core; todo lo que escribamos nosotros ya nace en español.
USE_I18N = True
LANGUAGE_CODE = "es"

# Catálogo de traducción propio. Django mergea los catálogos de LOCALE_PATHS
# DESPUÉS de los de las apps instaladas, con un dict.update() (ver
# django/utils/translation/trans_real.py, _add_local_translations), así que
# esto pisa string por string al catálogo que trae Evennia sin tocar
# site-packages. El .po se versiona; el .mo lo compila el entrypoint.
LOCALE_PATHS = [os.path.join(GAME_DIR, "locale")]

# Zona horaria del servidor (afecta logs y el admin de Django, no el reloj
# in-game, que se maneja con TIME_FACTOR / TIME_GAME_EPOCH más abajo).
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_TZ = True

######################################################################
# Reloj del mundo
######################################################################

# El ciclo día/noche es una mecánica de supervivencia, no decoración: de noche
# se ve menos, hace más frío y las cosas que hay afuera se mueven distinto.
#
# TIME_FACTOR = 4 => 1 día de juego cada 6 horas reales. Suficientemente rápido
# para que una sesión de una hora atraviese un cambio de luz, suficientemente
# lento para que "aguantar hasta el amanecer" siga significando algo.
TIME_FACTOR = 4.0

# Época del mundo: 1 de abril de 2033, 06:00 UTC. Unas semanas después del
# Brote. Fijarla (en vez de dejar None) hace que la fecha in-game sea canónica
# y no dependa de cuándo se levantó el server por primera vez.
TIME_GAME_EPOCH = 1995948000

# El tiempo de juego se congela cuando el server está caído. Es lo que queremos
# mientras desarrollamos: un reload no debe adelantar tres días de hambre.
TIME_IGNORE_DOWNTIMES = False

######################################################################
# Cuentas y personajes (modelo hardcore)
######################################################################

# Varias sesiones por cuenta compartiendo salida: cómodo para jugar desde el
# cliente web y un cliente telnet a la vez sin desconectarse solo.
MULTISESSION_MODE = 1

# Entrar y estar jugando, sin escalas. Al crear la cuenta se crea su personaje,
# y al identificarse se entra directo al mundo: no hay pantalla de selección ni
# hay que escribir `encarnar`.
#
# |yEsto es provisorio.|n La creación de personaje —origen, oficio, rasgos,
# taras— es parte del modelo hardcore y vuelve cuando exista el sistema de
# cuerpo (fase 1 de DISENO.md). Mientras no haya nada que elegir, un menú de
# selección con un solo personaje es una puerta que se abre a un pasillo.
AUTO_CREATE_CHARACTER_WITH_ACCOUNT = True
AUTO_PUPPET_ON_LOGIN = True

# Un sobreviviente vivo por cuenta. La permadeath la implementa el handler de
# muerte (archivar el personaje y liberar el cupo), no este número.
MAX_NR_CHARACTERS = 1
MAX_NR_SIMULTANEOUS_PUPPETS = 1

# Sin desconexión por inactividad: quedarse quieto y callado es una táctica
# válida cuando hay algo del otro lado de la puerta.
IDLE_TIMEOUT = -1

######################################################################
# Puertos de red (defaults de Evennia, explícitos para no adivinar después)
######################################################################

TELNET_PORTS = [4000]          # cliente MUD
WEBSERVER_PORTS = [(4001, 4005)]  # web (público, interno)
WEBSOCKET_CLIENT_PORT = 4002   # cliente web
AMP_PORT = 4006                # portal <-> server, interno

######################################################################
# Contenido del juego
######################################################################

# Módulos de prototipos: acá viven las definiciones de objetos spawneables
# (chatarra, comida en mal estado, armas improvisadas, mutágenos...).
PROTOTYPE_MODULES = ["world.prototypes"]

######################################################################
# Base de datos
######################################################################

# El juego corre en docker contra PostgreSQL (ver docker-compose.yml). Las
# credenciales llegan por entorno, nunca hardcodeadas ni versionadas.
#
# Si MIASMA_DB_HOST no está definida —por ejemplo, corriendo evennia a mano
# desde el .venv del host para una prueba rápida— se cae al sqlite3 por defecto
# de Evennia. Son dos bases distintas: no esperes ver los mismos datos.
if os.environ.get("MIASMA_DB_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("MIASMA_DB_NAME", "miasma"),
            "USER": os.environ.get("MIASMA_DB_USER", "miasma"),
            "PASSWORD": os.environ.get("MIASMA_DB_PASSWORD", ""),
            "HOST": os.environ["MIASMA_DB_HOST"],
            "PORT": os.environ.get("MIASMA_DB_PORT", "5432"),
            # Reusar conexiones: Evennia consulta la base en cada tick.
            "CONN_MAX_AGE": 600,
            "ATOMIC_REQUESTS": False,
        }
    }

######################################################################
# Desarrollo
######################################################################

# DEBUG se enciende por entorno (MIASMA_DEBUG=1 en .env). Nunca en un server
# expuesto: filtra settings y consultas SQL en la página de error.
DEBUG = os.environ.get("MIASMA_DEBUG", "0") == "1"

# Mostrar tracebacks in-game a quien tenga permiso de Developer, en vez de un
# "algo salió mal" inútil.
IN_GAME_ERRORS = True

######################################################################
# Punto de partida del mundo
######################################################################

# START_LOCATION y DEFAULT_HOME solo aceptan dbrefs, y los dbref cambian cada
# vez que se reconstruye el mapa. Por eso el constructor
# (world.mapa.constructor) escribe mapa_generado.py con los valores nuevos y
# acá se importan. Si el archivo no existe todavía —base recién creada, mapa
# sin construir— quedan los defaults de Evennia, que apuntan a Limbo.
try:
    from server.conf.mapa_generado import *
except ImportError:
    print("mapa_generado.py no encontrado: corré `batchcode batch.nebrida`.")

######################################################################
# secret_settings.py sobrescribe todo lo de arriba (y está en .gitignore)
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py no encontrado o falló al importar.")
