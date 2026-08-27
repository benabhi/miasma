# Notas para trabajar en este repo

## Lo esencial

- **El juego corre en Docker, no en el host.** Nunca ejecutes `evennia ...`
  directamente desde `.venv/`: apunta a otra base (sqlite) y no es el entorno
  real. Usá `docker compose exec game evennia ...`.
- **`.venv/` existe solo para el editor** (autocompletado y linting).
- **El código del juego vive en `miasma/`** y está montado dentro del
  contenedor en `/usr/src/game`. Editar en el host es suficiente.

## Comandos

```bash
docker compose exec game evennia reload      # recargar código del juego
docker compose restart game                  # tras tocar settings.py
docker compose exec game evennia shell       # consola con el juego cargado
docker compose exec game evennia test --settings settings.py .
docker compose logs -f game
```

## Convenciones

- **Todo el contenido de cara al jugador va en español rioplatense** (voseo):
  descripciones, mensajes de error, ayuda, nombres de comandos. `LANGUAGE_CODE`
  está en `"es"`.
- **Código y comentarios en español.** Nombres de clases y funciones en inglés
  cuando son de la API de Evennia (`at_object_creation`, `return_appearance`);
  los propios, en español.
- **No corras `makemigrations`.** Los avisos de migraciones pendientes al
  arrancar son proxy models de Evennia, cosméticos. Generarlas escribiría en
  `site-packages` del contenedor y se perdería en el siguiente build.
- **Los secretos van a `.env`** (no versionado). Al agregar una variable nueva,
  agregarla también a `.env.example`.
- `docker/entrypoint.sh` debe conservar finales de línea **LF** (ya está
  forzado en `.gitattributes`).

## El mapa

El mundo se genera desde datos, no se construye a mano in-game. Para agregar o
cambiar salas se edita `world/mapa/silent_hill.py` y se reconstruye:

```bash
docker compose exec game evennia shell -c "from world.mapa.constructor import construir; construir()"
docker compose restart game
```

El reinicio no es opcional: el punto de partida cambia de dbref en cada
reconstrucción y vive en `server/conf/mapa_generado.py`, que es un archivo de
settings. `docs/MAPA.md` tiene la traza completa y el formato de los datos.

Nunca crear salas del mapa con `dig`/`tunnel` in-game: la próxima
reconstrucción no las va a conocer y quedan colgadas.

## Diseño

`docs/DISENO.md` tiene los pilares, la hoja de ruta por fases y las decisiones
ya tomadas. Antes de proponer un sistema nuevo, chequear en qué fase cae y si
contradice algún pilar.
