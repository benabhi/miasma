# Imagen del servidor de Miasma.
#
# La imagen contiene SOLO el runtime (Python + Evennia + driver de Postgres).
# El código del juego NO se copia acá: se monta desde el host en /usr/src/game
# (ver docker-compose.yml). Así se edita en el editor de siempre y un `evennia
# reload` levanta los cambios sin reconstruir la imagen.

FROM python:3.12-slim

# EVENNIA_VERSION es el único lugar donde se fija la versión del framework.
ARG EVENNIA_VERSION=6.1.0

ENV PYTHONUNBUFFERED=1 \
    # Evita que el contenedor ensucie el bind mount con __pycache__ de root.
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# procps:  Evennia inspecciona procesos al arrancar/parar sus dos servicios.
# gettext: msgfmt compila el catálogo de traducción en cada arranque;
#          xgettext y msgmerge lo regeneran cuando cambia la versión de Evennia.
RUN apt-get update \
    && apt-get install -y --no-install-recommends procps gettext \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install "evennia==${EVENNIA_VERSION}" "psycopg[binary]~=3.2"

WORKDIR /usr/src/game

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# 4000 telnet (cliente MUD) | 4001 web | 4002 websocket (cliente web)
EXPOSE 4000 4001 4002

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# -l deja Evennia en primer plano volcando los logs a stdout, que es lo que
# docker espera para poder hacer `docker compose logs -f`.
CMD ["evennia", "-l", "start"]
