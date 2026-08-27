#!/usr/bin/env bash
# Prepara el gamedir montado y arranca lo que venga en CMD.
set -euo pipefail

cd /usr/src/game

# 1. Restos de un contenedor que murió sin apagar Evennia limpiamente.
#    Si quedan, el launcher cree que ya hay un server vivo y se niega a arrancar.
rm -f server/*.pid server/*.restart 2>/dev/null || true

# 2. Crear server/logs/ y server/conf/secret_settings.py si faltan.
#    El SECRET_KEY se genera acá y queda en el host (está en .gitignore).
evennia --initmissing || true

# 3. Esperar a Postgres. El healthcheck de compose ya lo cubre, pero un reinicio
#    de la base con el juego arriba no debería tumbar el contenedor.
if [ -n "${MIASMA_DB_HOST:-}" ]; then
    echo "==> esperando a Postgres en ${MIASMA_DB_HOST}:${MIASMA_DB_PORT:-5432} ..."
    python - <<'PY'
import os, sys, time
import psycopg

dsn = "host={host} port={port} dbname={db} user={user} password={pwd}".format(
    host=os.environ["MIASMA_DB_HOST"],
    port=os.environ.get("MIASMA_DB_PORT", "5432"),
    db=os.environ.get("MIASMA_DB_NAME", "miasma"),
    user=os.environ.get("MIASMA_DB_USER", "miasma"),
    pwd=os.environ.get("MIASMA_DB_PASSWORD", ""),
)
for intento in range(1, 61):
    try:
        with psycopg.connect(dsn, connect_timeout=3):
            print("==> Postgres responde.")
            sys.exit(0)
    except Exception as err:
        print(f"    ... intento {intento}/60: {err.__class__.__name__}")
        time.sleep(2)
print("!! Postgres no respondió a tiempo.", file=sys.stderr)
sys.exit(1)
PY
fi

# 4. Migraciones. Idempotente: si no hay nada nuevo, no hace nada.
echo "==> aplicando migraciones ..."
evennia migrate --noinput

# 5. Aviso: si no existe la Cuenta #1 y no hay credenciales en el entorno,
#    Evennia abre un prompt interactivo y el contenedor se cuelga esperando
#    algo que nadie va a tipear. Las variables EVENNIA_SUPERUSER_* son el
#    mecanismo propio del framework para crearla sin interacción (las lee
#    evennia_launcher.create_superuser); solo actúa si la cuenta no existe.
if [ -z "${EVENNIA_SUPERUSER_USERNAME:-}" ] || [ -z "${EVENNIA_SUPERUSER_PASSWORD:-}" ]; then
    echo "!! EVENNIA_SUPERUSER_USERNAME / _PASSWORD sin definir en .env."
    echo "   Si la Cuenta #1 todavía no existe, este arranque se va a colgar."
fi

echo "==> arrancando: $*"
exec "$@"
