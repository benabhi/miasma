# Traducción al español

Miasma se juega en español rioplatense. La traducción tiene **dos mecanismos
distintos**, y saber cuál toca es lo primero que hay que decidir antes de
cambiar un texto.

| Si el texto sale de… | Se traduce en… |
|---|---|
| el motor de Evennia (descripción de sala, salidas, movimiento, login, errores) | `miasma/locale/es/LC_MESSAGES/django.po` |
| un comando (su nombre, su ayuda, sus mensajes) | `miasma/commands/*.py` |
| el mundo (salas, objetos) | `miasma/world/mapa/nebrida.py` |

---

## 1. El catálogo del motor

Evennia envuelve parte de sus strings en `gettext`. Ese catálogo **no se toca en
`site-packages`**: el gamedir tiene el suyo y Django lo mergea por encima.

Django arma los catálogos en este orden
(`django/utils/translation/trans_real.py`): primero los de las apps instaladas
—entre ellas Evennia—, después los de `LOCALE_PATHS`, con un `dict.update()`.
Como el nuestro va último, gana string por string. `settings.py` lo declara así:

```python
LOCALE_PATHS = [os.path.join(GAME_DIR, "locale")]
```

**Estado: 221 de 221 strings traducidos.** El catálogo que trae Evennia en
español estaba al 27% y desactualizado desde 2022 (le faltaban msgids tan
visibles como `Exits`, `Characters` y `You see`), así que se regeneró entero.

### Cambiar una traducción

Editar el `.po` y reiniciar el contenedor. El `.mo` —que es lo único que Django
lee— lo compila el entrypoint en cada arranque, por eso no se versiona:

```bash
docker compose restart game
```

### Regenerar el catálogo tras actualizar Evennia

Una versión nueva trae msgids nuevos. Dentro del contenedor:

```bash
docker compose exec game bash
cd /usr/local/lib/python3.12/site-packages/evennia
find . -name "*.py" -not -path "./contrib/*" -not -name "tests.py" -not -path "*/tests/*" > /tmp/fuentes.txt
xgettext --language=Python --keyword=_ --from-code=UTF-8 --files-from=/tmp/fuentes.txt -o /tmp/evennia.pot
msgmerge --no-fuzzy-matching /usr/src/game/locale/es/LC_MESSAGES/django.po /tmp/evennia.pot -o /usr/src/game/locale/es/LC_MESSAGES/django.po
msgfmt --statistics -o /dev/null /usr/src/game/locale/es/LC_MESSAGES/django.po
```

`msgmerge` conserva lo ya traducido y deja vacíos los msgids nuevos. Lo que
quede marcado `fuzzy` hay que revisarlo a mano: es una traducción vieja que
`msgmerge` adivinó, y suele tener los placeholders del formato viejo (`%s` en
vez de `{key}`).

`miasma/locale/evennia.pot` es la plantilla generada; se versiona para poder
diffear qué cambió entre versiones de Evennia.

---

## 2. Los comandos

Los comandos **no se pueden traducir por gettext**: los módulos de
`evennia/commands/default/` tienen 6 llamadas a `_()` en total sobre ~90
comandos, y `general.py` y `account.py` no tienen ninguna. El `key` de cada
comando es un string literal. Traducir un comando es subclasearlo.

| Archivo | Qué contiene |
|---|---|
| `commands/jugador.py` | comandos del personaje: mirar, tomar, soltar, dar, inventario, decir, susurrar, gesto, describirme, casa, apodo, ayuda |
| `commands/cuenta.py` | comandos de cuenta: salir, encarnar, desencarnar, crearpj, borrarpj, contrasena, quien, sesiones, atenuar, estilo, opciones, color, privado |
| `commands/sin_loguear.py` | antes de identificarse: conectar, crear, salir, ayuda, mirar, codificacion, lector |
| `commands/default_cmdsets.py` | saca los originales y pone los nuestros |

### Reglas

- **El nombre en inglés queda siempre como alias.** `mirar` y `look` hacen lo
  mismo; el que se muestra en la ayuda es el español. Así los ejemplos de la
  documentación de Evennia siguen funcionando.
- **El docstring es la ayuda.** Evennia arma la entrada de ayuda con el
  `__doc__` de la clase, así que se escribe en español y con el `Uso:` en
  español.
- **`help_category` en minúscula.** Evennia la baja a minúsculas al crear la
  clase (`commands/command.py:104`), así que `general` y `General` son la misma
  categoría y no se duplican en el índice.

### Agregar un comando traducido

1. Subclasear el original en el módulo que corresponda, cambiando `key`,
   `aliases` (¡con el nombre en inglés adentro!), `help_category` y el
   docstring.
2. En `default_cmdsets.py`, sumar el key original a la tupla de los que se
   quitan y la clase nueva a la de los que se agregan.

**El `remove()` no es opcional.** Si el original se queda en el cmdset, Evennia
ve dos candidatos para `look` —el key del original y el alias del nuestro— y
responde un multimatch en vez de ejecutar. La señal de que faltó un `remove()`
es ver comandos duplicados en el índice de `ayuda`.

---

## 3. Plurales

Evennia usa `inflect` (inglés) para armar los nombres numerados, lo que producía
`an una lata de duraznos` y `two latas`. `typeclasses/objects.py` sobrescribe
`get_numbered_name` en el mixin `ObjectParent`, así que aplica a objetos,
salidas, personajes y salas:

- **El singular es el nombre tal cual**, sin artículo: en español el artículo lo
  pone el constructor dentro del nombre.
- **El plural** antepone el número y pluraliza desde la primera palabra hasta la
  primera preposición, que es donde termina el núcleo del sintagma:
  `cuchillo oxidado` → `2 cuchillos oxidados`, `lata de duraznos` →
  `3 latas de duraznos`.

`pluralizar()` cubre las reglas regulares. No maneja la pérdida de tilde
(`canción` → `canciones`); para esos casos conviene elegir otro nombre.

---

## Deuda conocida

- **Tres comandos están traducidos solo en nombre y ayuda, y su salida sigue
  en inglés**: `apodo` (254 líneas en Evennia), `opciones` (177) y `color`
  (170), más `privado` (242) y `codificacion` (84). Son los más largos del
  framework y copiar su `func()` para traducir un puñado de mensajes deja mucho
  código que se desincroniza en cada actualización. Cada uno lo avisa en su
  propia ayuda con una nota en amarillo.
- **Los comandos de construcción y administración quedan en inglés** a
  propósito: `@dig`, `@create`, `@teleport`, `ban`, `boot`, `perm`… Los usa el
  staff y así siguen alineados con la documentación de Evennia. Sus categorías
  de ayuda (`Admin`, `Building`, `Comms`) también.
- **Los switches siguen en inglés** (`@teleport/quiet`, `salir/all`).
- **Los `func()` copiados hay que revisarlos al actualizar Evennia.** Los
  comandos que solo cambian nombre y ayuda no tienen ese problema; los que
  reescriben `func()` sí. Están todos en los tres módulos de `commands/`.
- **El catálogo completo se podría aportar upstream** a Evennia: pasó de 27% a
  100% y está regenerado contra 6.1.0. Es un PR aparte.
