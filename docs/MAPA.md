# El mundo: Silent Hill

Escenario de pruebas de Miasma: una reconstrucción de la ciudad de *Silent Hill*
(Konami, 1999). No es contenido definitivo — es un mundo conocido y de tamaño
razonable sobre el que probar cada sistema nuevo a medida que se incorpora.

**309 salas, 1091 salidas, 5 planos.** El juego arranca en el Café 5to2.

---

## Reconstruirlo

Todo el mundo se genera desde datos. Reconstruirlo es un comando, y es
idempotente: borra lo que dejó la corrida anterior y levanta todo de cero.

Desde el juego, como superusuario:

```
batchcode batch.silent_hill
```

Desde la línea de comandos:

```bash
docker compose exec game evennia shell -c "from world.mapa.constructor import construir; construir()"
```

**Después de reconstruir hay que reiniciar el server**, porque el punto de
partida cambia de dbref:

```bash
docker compose restart game
```

### Por qué hace falta el reinicio

`START_LOCATION` y `DEFAULT_HOME` de Evennia solo aceptan dbrefs (`"#708"`), y
los dbrefs cambian en cada reconstrucción. Por eso el constructor escribe
`server/conf/mapa_generado.py` con los valores nuevos y `settings.py` lo
importa. Como es un archivo de settings, un `evennia reload` no alcanza.

`mapa_generado.py` no se versiona: los dbrefs son propios de cada base de datos.

---

## La grilla

El mundo es **una grilla densa**: cada celda es una sala por la que se camina, o
terreno que se dibuja pero no se pisa (agua, arboleda, muro). No hay huecos. Se
puede ir de una punta del pueblo a la otra caminando en cualquier dirección.

Cada plano se dibuja como una imagen de texto en `world/mapa/ubicaciones.py`,
un carácter por celda:

```python
PUEBLO = """
TTTTTTTTTd~~TTTTTTTT
xccxccxcca~~xccxccaT
chhchhcssa~~cPPcssaT
chhchhcdda~~cPPcseaT
xccxccxcca~~xccxccaT
chhchhcssa~~csscHHaT
chlchdcgga~~csdcHHaT
xccxccxcca~~xccxccaT
csscEEciga~~ceeceeaT
csdcEEciga~~ceeceeaT
xccxccxccappxccVccaT
~~~~~~~~~~~~ceecMMaT
~~~~~~~~~~~~ceecMMaT
~~~~~~~~~~~~xccxcca*
~~~~~~~~~~~~chhcssaT
~~~~~~~~~~~~chhcssaT
~~~~~~~~~~~pxccxccaT
~~~~~~~~~~~~csdcsMaT
~~~~~~~~~~~~csdcMMaT
~~~~~~~~~~~!xccxccaT
~~~~~~~~~~~~cddcddaT
~~~~~~~~~~~~cddcddaT
~~~~~~~~~~~&xccxccaT
"""
```

La primera línea es la del norte y el primer carácter de cada línea el del
oeste, así que la imagen se lee como el mapa. `LEYENDA` traduce cada carácter a
un tipo de sala.

**Las salidas norte/sur/este/oeste no se escriben.** El constructor conecta cada
celda con sus vecinas ortogonales. Lo que sí se declara a mano en `CONEXIONES`
son las salidas que no son de grilla: entrar a un negocio (`café`, `iglesia`),
subir un piso (`arriba`), cruzar de plano (`escuela`, `hospital`). Una salida
escrita a mano siempre le gana a la automática.

### Salas con nombre y salas de relleno

- Las salas escritas en `silent_hill.py` reclaman su celda en `NOMBRADAS`, y
  usan su nombre y su descripción propios. Son 96.
- Las celdas que no reclamó nadie las llena el constructor con salas genéricas
  según el tipo, desde la tabla `RELLENO` ("Calzada", "Baldío", "Casa
  abandonada"…). Son 205. Existen para que la grilla quede densa sin tener que
  escribir doscientas descripciones; el detalle está en las salas con nombre.
- `ANCLADAS` son los interiores de una sola sala. No ocupan celda: dibujar un
  mapa de 1×1 para el interior de un bar no le sirve a nadie, así que cuando el
  jugador está adentro se dibuja la calle de la que entró, con la marca sobre
  esa celda. Son 8 —la torre del puente, la habitación y el garage del motel,
  la enfermería y el aula de la escuela— y el constructor resuelve el ancla
  solo, mirando de dónde se entra.

### El agua no es una sala

El lago Toluca, el canal del puente levadizo y las paredes interiores se
dibujan (`~`, `█`) pero no son salas. La alternativa —hacerlos caminables— sería
peor: un MUD de supervivencia donde se camina sobre el lago no es más denso, es
menos creíble. El vacío del mapa se llena con terreno visible, no con salas
imposibles.

---

## El minimapa

Cada `mirar` sale en dos columnas: el minimapa a la izquierda, el nombre y la
descripción a la derecha, y debajo —a todo el ancho— las salidas, los personajes
y las cosas. Se redibuja solo en cada movimiento, porque lo arma
`Room.return_appearance()` (`typeclasses/rooms.py`).

```
┌─────────────┐   Café 5to2
│T T T T . ~ ~│
│░ ▒ ░ ░ ▓ ~ ~│   Un bar de esquina de doce mesas, con piso de damero y bancos
│n ░ $ @ ▓ ~ ~│   de cuerina roja rajada. La vidriera que da a Finney está
│n ░ . . ▓ ~ ~│   reventada hacia adentro y el vidrio cruje bajo cualquier
│░ ▒ ░ ░ ▓ ~ ~│   paso.
│n ░ $ $ ▓ ~ ~│
│. ░ % % ▓ ~ ~│   Sobre el mostrador, junto a una taza con café frío y una
└─────────────┘   raya de carmín en el borde, hay una radio portátil...
Salidas: fuera, norte, sur y oeste
```

El radio es de 3 celdas: con la calle cada tres, entra una manzana entera con
sus calles alrededor, que es lo mínimo para orientarse en una retícula.

`mapa` (alias `map`) muestra el plano entero con una referencia de símbolos.
Acepta un radio: `mapa 5`.

### Ancho fijo, alto variable

El minimapa usa una ventana de tamaño fijo que se corre para no asomarse fuera
del plano, como una cámara con límites. Si se recortara a lo que existe, el
ancho cambiaría de sala en sala y la columna de texto bailaría a cada paso.

El **alto** sí varía: entre dos filas de celdas se dibuja una fila separadora
solo si tiene algún muro. Una fila separadora sin muros es una línea en blanco
que ocupa alto y no dice nada.

### Los muros los dicen las salidas, no los datos

`world/mapa/render.py` no dibuja desde `ubicaciones.py`: recorre las **salidas
reales** de cada sala. Entre dos celdas contiguas pone un espacio si hay paso y
un muro si no. Si abrís un pasaje nuevo in-game, el mapa lo refleja sin tocar
ningún dato.

Un muro solo se dibuja entre dos salas que existen y no se comunican.

### Sobre los caracteres

La primera versión usaba formas geométricas y símbolos lindos (`▤ ▣ ✚ ⦿ † ◊`) y
en la práctica salían cuadraditos vacíos: las fuentes monoespaciadas que usan
los clientes MUD no cubren esos bloques Unicode. Un mapa ilegible no sirve por
más elegante que sea el carácter, así que `world/mapa/iconos.py` se limita a:

- **bloques de sombreado** (`░ ▒ ▓ █`) y **dibujo de cajas** (`─ │ ═ ║ ╬`), que
  vienen de CP437 y están en cualquier fuente monoespaciada;
- **ASCII puro** para todo lo demás, al estilo de los roguelikes: `#` edificio,
  `$` comercio, `+` iglesia, `@` el jugador.

Si algún día usás una fuente con buena cobertura Unicode (Fira Code, Cascadia,
DejaVu Sans Mono), cambiar `iconos.py` alcanza para volver a los símbolos
bonitos: nada más lee esos caracteres.

Los emoji quedan descartados siempre, con cualquier fuente: ocupan dos columnas
y descuadran la grilla entera.

---

## Los archivos

| Archivo | Qué es |
|---|---|
| `world/mapa/ubicaciones.py` | **La grilla.** El dibujo de cada plano, qué sala ocupa cada celda y con qué rellenar las que sobran. |
| `world/mapa/silent_hill.py` | **Los textos.** Nombres, descripciones y las conexiones que no son de grilla. |
| `world/mapa/iconos.py` | Tipos de sala a caracteres, y los muros. |
| `world/mapa/render.py` | Dibuja el mapa recorriendo las salidas reales. |
| `world/mapa/constructor.py` | Valida, borra el mundo anterior, construye el nuevo, escribe los dbrefs. |
| `world/batch/silent_hill.py` | Punto de entrada del batchprocessor. Tres líneas. |

### Agregar una sala con nombre propio

1. En `ubicaciones.py`, poner el carácter de su tipo en la celda del dibujo.
2. En `silent_hill.py`, la entrada en `SALAS`:

```python
SALAS["int_farmacia"] = {
    "nombre": "Farmacia de Bloch St.",
    "distrito": "old",
    "exterior": False,        # True antepone la niebla a la descripción
    "desc": "...",
}
```

3. En `ubicaciones.py`, reclamar la celda:

```python
NOMBRADAS["int_farmacia"] = ("pueblo", 2, 6, 0)
```

Si es un interior de una sola sala, en vez del paso 3 va en `ANCLADAS` con su
tipo, y en `CONEXIONES` la salida con nombre que lleva hasta ahí.

**No hace falta declarar norte/sur/este/oeste**: eso lo hace el constructor.

### Las validaciones

`constructor.validar()` corre antes de tocar la base y aborta sin construir nada
si encuentra:

- un carácter del dibujo que no está en `LEYENDA`,
- un tipo transitable sin entrada en `RELLENO`,
- una sala con nombre que cae fuera del dibujo, sobre agua, o encima de otra,
- una sala escrita que no está ni en `NOMBRADAS` ni en `ANCLADAS`, o que está en
  las dos,
- dos salidas con el mismo nombre en la misma sala,
- cualquier sala inalcanzable caminando desde el punto de partida.

### Qué se borra y qué no

El constructor etiqueta todo lo que crea con `silent_hill` (categoría `mapa`) y
solo borra objetos con esa etiqueta, más las salas de ejemplo de Evennia
(Limbo). Lo que hayas dejado tirado dentro de una sala se pierde con la sala,
pero **los personajes y los objetos que estén ahí se mudan al punto de partida
antes del borrado**, no se destruyen.

---

## La traza

Reconstruida desde los mapas in-game y las guías de
[silenthillmemories.net](https://www.silenthillmemories.net/sh1/). Los nombres
de calles, comercios y salas interiores son los del juego. La topología es una
simplificación navegable: las calles se representan por sus cruces, no metro a
metro.

El pueblo entero es **un solo plano continuo**: Old Silent Hill al noroeste, el
canal en el medio con el puente levadizo, el centro al este y el área turística
bajando hacia el lago Toluca. Hay calle cada tres celdas en los dos ejes, y
entre ellas las manzanas de 2×2.

```
T T T T T T T T T . ~ ~ T T T T T T T T
▒ ░ ░ ▒ ░ ░ ▒ ░ ░ ▓ ~ ~ ▒ ░ ░ ▒ ░ ░ ▓ T
░ n n ░ n n ░ $ $ ▓ ~ ~ ░ P P ░ $ $ ▓ T
░ n n ░ n n ░ . . ▓ ~ ~ ░ P P ░ $ # ▓ T
▒ ░ ░ ▒ ░ ░ ▒ ░ ░ ▓ ~ ~ ▒ ░ ░ ▒ ░ ░ ▓ T
░ n n ░ n n ░ $ $ ▓ ~ ~ ░ $ $ ░ H H ▓ T
░ n : ░ n . ░ % % ▓ ~ ~ ░ $ . ░ H H ▓ T
▒ ░ ░ ▒ ░ ░ ▒ ░ ░ ▓ ~ ~ ▒ ░ ░ ▒ ░ ░ ▓ T
░ $ $ ░ E E ░ + % ▓ ~ ~ ░ # # ░ # # ▓ T
░ $ . ░ E E ░ + % ▓ ~ ~ ░ # # ░ # # ▓ T
▒ ░ ░ ▒ ░ ░ ▒ ░ ░ ▓ = = ▒ ░ ░ v ░ ░ ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ # # ░ M M ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ # # ░ M M ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ▒ ░ ░ ▒ ░ ░ ▓ *
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ n n ░ $ $ ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ n n ░ $ $ ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ = ▒ ░ ░ ▒ ░ ░ ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ $ . ░ $ M ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ $ . ░ M M ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ! ▒ ░ ░ ▒ ░ ░ ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ . . ░ . . ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ░ . . ░ . . ▓ T
~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ & ▒ ░ ░ ▒ ░ ░ ▓ T
```

La escuela, el hospital, las alcantarillas y el parque tienen plano propio, con
sus niveles:

| Plano | Niveles | Qué tiene |
|---|---|---|
| Escuela Midwich | sótano, PB, 1º, azotea | patio con torre de reloj, laboratorio, sala de música, biblioteca, caldera |
| Hospital Alchemilla | −2 a +2 | planta baja completa, sala de máquinas, pisos por ascensor |
| Alcantarillas | −1 y 0 | túneles, cruce de galerías, oficina, pasarela superior |
| Lakeside Amusement Park | 0 | calesita, vuelta al mundo, montaña rusa, heladería |

---

## Deuda conocida

- Las descripciones son estáticas. Cuando exista el sistema de luz y clima
  (fase 3 de `DISENO.md`), las salas de exterior deberían describir distinto de
  día y de noche, y la constante `NIEBLA` debería salir de ahí.
- No hay puertas ni cerraduras: todas las salidas están abiertas. Las que en el
  juego original están cerradas con llave (la azotea de la escuela, la reja de
  las alcantarillas, Indian Runner) están descritas como cerradas pero se
  cruzan igual.
- No hay objetos ni NPCs. El mundo es geografía pura.
- El minimapa no marca las escaleras: si una sala tiene salidas hacia otro
  nivel, hay que entrar para enterarse. `mapa` sí dice en qué nivel estás y
  cuántos tiene el plano.
- Las 205 salas de relleno comparten descripción por tipo: hay muchas
  "Calzada" idénticas. A medida que el pueblo importe, conviene irlas
  ascendiendo a salas con nombre propio; el andamiaje ya está.
