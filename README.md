# Miasma

MUD de supervivencia hardcore. Post-Brote, zombis y mutaciones, al estilo
*Cataclysm: Dark Days Ahead*: sin héroes, sin puntos de guardado, y el clima,
el hambre y una herida mal curada matan más que los muertos.

Construido sobre [Evennia](https://www.evennia.com/) 6.1.0.

---

## Cómo está armado

El **stack corre en Docker**; el **código vive en el host** y se monta dentro
del contenedor. La imagen solo aporta el runtime (Python 3.12 + Evennia +
driver de Postgres): no contiene código del juego. Editás en `./miasma/` con tu
editor de siempre y un `evennia reload` levanta los cambios sin reconstruir
nada.

```
.
├── docker-compose.yml     el stack: db + game
├── docker/
│   ├── Dockerfile         runtime: python:3.12-slim + evennia + psycopg
│   └── entrypoint.sh      limpia pids, espera la db, migra, arranca
├── .env                   secretos locales (NO versionado)
├── .env.example           plantilla de .env
├── docs/
│   ├── DISENO.md          pilares de diseño y hoja de ruta de sistemas
│   ├── TRADUCCION.md      cómo y dónde se traduce cada cosa
│   └── MAPA.md            el escenario de pruebas y cómo reconstruirlo
├── miasma/                ← EL GAMEDIR. Todo el código del juego.
│   ├── commands/          comandos propios y cmdsets
│   ├── typeclasses/       Character, Room, Object, Exit, Script
│   ├── world/             contenido: mapa, prototipos, batches
│   ├── web/               cliente web, website, API
│   └── server/conf/       settings.py y demás configuración
└── .venv/                 Python del host, SOLO para autocompletado del editor
```

| Servicio | Contenedor    | Qué es                                    |
|----------|---------------|-------------------------------------------|
| `db`     | `miasma-db`   | PostgreSQL 17. Datos en el volumen `miasma_db_data`. Sin puerto publicado. |
| `game`   | `miasma-game` | Evennia. Publica 4000 / 4001 / 4002.      |

---

## Arranque desde cero

Requiere solo Docker Desktop.

```bash
cp .env.example .env      # y editar: contraseñas propias
docker compose up -d --build
docker compose logs -f game
```

El primer arranque tarda: migra la base y crea la Cuenta #1 y Limbo.

Cuando en los logs aparezca `Evennia Server successfully started`:

- **Cliente MUD (telnet):** `localhost` puerto `4000`
- **Web y cliente web:** <http://localhost:4001>
- **Admin de Django:** <http://localhost:4001/admin/>

La cuenta de administrador es la que pusiste en `.env`
(`EVENNIA_SUPERUSER_USERNAME` / `EVENNIA_SUPERUSER_PASSWORD`). Evennia la crea
sola en el primer arranque, cuando detecta que no existe la Cuenta #1.

---

## El cliente

El cliente oficial es [TinTin++](https://tintin.mudhalla.net/). El repo trae
`miasma.tin`, que deja la pantalla partida con el mapa arriba, el automapper
andando y el teclado numérico moviendo al personaje:

```bash
tt++ miasma.tin
```

| Tecla | Va a |
|---|---|
| `8` `2` `4` `6` | norte, sur, oeste, este |
| `7` `9` `1` `3` | las diagonales |
| `5` | mirar |
| `0` | mapa |

El numérico manda esas secuencias con **Bloq Num apagado**. Con Bloq Num
encendido escribe dígitos, y para ese caso están los alias `8`, `2`, `4`… que
hacen lo mismo apretando Enter.

**La ciudad viene dibujada.** `miasma/nebrida.map` se genera desde el mundo
del juego y el cliente lo carga al conectarse, así que el mapa está completo
desde el primer minuto y no se dibuja solo mientras caminás.

> **Arrancá TinTin++ parado en la raíz del repo.** La ruta del mapa es relativa
> al directorio desde el que lo levantás, no a `miasma.tin`. Si lo arrancás
> desde otro lado vas a ver `#MAP READ: FILE {miasma/nebrida.map} NOT FOUND.`;
> se arregla poniendo la ruta completa en la variable `miasma[mapa]`, arriba de
> todo en `miasma.tin`.

Para regenerarlo tras cambiar el mundo:

```bash
docker compose exec game evennia shell -c "from world.mapa.exportar_tintin import exportar; exportar()"
```

Otros atajos: `ira <lugar>` camina solo hasta un lugar del mapa,
`mapaubicar <sala>` reubica el cursor si entraste lejos de la Plaza Mayor,
`mapadeshacer` deshace el último paso, `mapacargar` recarga el mapa, `clear`
limpia la pantalla.

---

## El día a día

```bash
# recargar el código del juego tras editar (rápido, no corta sesiones)
docker compose exec game evennia reload

# reinicio completo (necesario al tocar settings.py)
docker compose restart game

# ver logs
docker compose logs -f game

# consola de Python con el juego cargado
docker compose exec game evennia shell

# tests
docker compose exec game evennia test --settings settings.py .

# shell dentro del contenedor
docker compose exec game bash

# parar / levantar
docker compose stop
docker compose up -d
```

**`reload` vs `restart`:** `evennia reload` recarga typeclasses, comandos y
scripts sin desconectar a nadie; es lo que vas a usar el 95% del tiempo. Los
cambios en `settings.py` necesitan `docker compose restart game`.

### Reconstruir la imagen

Solo hace falta al cambiar `docker/Dockerfile` o la versión de Evennia en
`.env`:

```bash
docker compose build --no-cache game && docker compose up -d
```

### Borrar la base y empezar de nuevo

Destruye todo el mundo y todas las cuentas:

```bash
docker compose down -v
docker compose up -d
```

---

## El mapa de pruebas

El mundo actual es **Nébrida**: una ciudad mediana de provincia sobre un lago,
partida por un río, con centro cívico, barrios, puerto y zona de galpones.
80×40 celdas, 2452 salas y 9326 salidas, con retícula de calles, avenidas, una
diagonal, tres puentes y bosque en las afueras. El juego arranca en la Plaza
Mayor.

Se genera entero desde datos y se reconstruye con un comando:

```bash
docker compose exec game evennia shell -c "from world.mapa.constructor import construir; construir()"
docker compose restart game
```

o, desde el juego y como superusuario, `batchcode batch.nebrida` (el reinicio
hace falta igual). Detalles, traza y cómo agregar salas en
[`docs/MAPA.md`](docs/MAPA.md).

---

## Idioma

El juego se juega en español. Los comandos de jugador tienen nombre español
(`mirar`, `tomar`, `inventario`, `decir`, `ayuda`) y **conservan el nombre en
inglés como alias**, así que `look` sigue funcionando.

Los mensajes del motor salen de un catálogo propio del gamedir
(`miasma/locale/es/LC_MESSAGES/django.po`, 221/221 strings) que pisa al de
Evennia sin tocar `site-packages`. El `.mo` lo compila el entrypoint en cada
arranque, así que **cambiar una traducción necesita reiniciar**, no alcanza con
`reload`:

```bash
docker compose restart game
```

Los comandos, en cambio, son código: con `evennia reload` alcanza. Detalles y
deuda conocida en [`docs/TRADUCCION.md`](docs/TRADUCCION.md).

---

## Entorno del editor (opcional)

`./.venv/` es un virtualenv de Windows con Evennia 6.1.0 instalado. **El juego
no corre desde ahí**: existe para que el editor resuelva imports, autocomplete
y el linter no marque `evennia` en rojo. Apuntá el intérprete de tu editor a
`.venv\Scripts\python.exe`.

Si lo perdés, se rehace con:

```bash
py -3.12 -m venv .venv
.venv/Scripts/python -m pip install evennia==6.1.0
```

---

## Notas

- **`settings.py` lee la base del entorno.** Si `MIASMA_DB_HOST` no está
  definida cae a sqlite3, que es lo que pasaría corriendo Evennia a mano desde
  el `.venv` del host. Son dos bases distintas: la de verdad es la de Docker.
- **Aviso de migraciones pendientes en el arranque.** Evennia reporta cambios
  no migrados en `accounts`, `comms`, `objects`, `scripts` y `typeclasses`. Son
  *proxy models* (no tocan el esquema) más un renombre de índice, todo dentro
  del propio Evennia. Es cosmético. **No corras `makemigrations`**: escribiría
  dentro de `site-packages` del contenedor y se perdería en el siguiente build.
- **`.env` no se versiona.** Al clonar el repo en otra máquina hay que crearlo
  desde `.env.example`.
- **`server/conf/secret_settings.py`** lo genera Evennia con un `SECRET_KEY`
  propio de cada instalación, y está en `.gitignore`.
