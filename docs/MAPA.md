# El mundo: Nébrida

Nébrida es una ciudad mediana de provincia sobre un lago, partida por un río,
con su centro cívico, sus barrios, su puerto y su zona de galpones. Es el
escenario sobre el que se prueba cada sistema nuevo a medida que se incorpora.

**1541 salas, 4512 salidas, 3 planos.** El juego arranca en la Plaza Mayor, y
se entra directo: al identificarse ya estás jugando.

El mapa es de 80×40 celdas. La retícula tiene separaciones desparejas —manzanas
de dos, tres y cuatro celdas mezcladas— más una avenida diagonal que corta el
damero: una ciudad con todas las manzanas iguales se lee como papel
cuadriculado.

---

## Reconstruirlo

Todo el mundo se genera desde datos. Reconstruirlo es un comando, y es
idempotente: borra lo que dejó la corrida anterior y levanta todo de cero.

Desde el juego, como superusuario:

```
batchcode batch.nebrida
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

- Las salas escritas en `nebrida.py` reclaman su celda en `NOMBRADAS`, y usan
  su nombre y su descripción propios. Son 27: los lugares singulares.
- Las celdas que no reclamó nadie las llena el constructor con salas genéricas
  según el tipo, desde la tabla `RELLENO` ("Calzada", "Baldío", "Casa
  abandonada"…). Son 2425. Cada tipo tiene varias variantes y el constructor
  elige una según la coordenada, así que dos manzanas seguidas no dicen lo
  mismo. **Los tramos de calle se llaman como la calle**: "Calle Rovira",
  "Calle Undiano y Calle Bergara". Una ciudad no necesita dos mil descripciones
  distintas; necesita que cada esquina sepa cómo se llama.
- `ANCLADAS` es para interiores de una sola sala, que no ocupan celda: cuando
  el jugador está adentro se dibuja la calle de la que entró. Hoy está vacío:
  todo lo visitable ocupa su lugar en algún plano.

### Los edificios no se atraviesan

Una manzana de departamentos no es un terreno por el que se pasa. De cada grupo
de celdas contiguas del mismo tipo, el constructor hace sala **una sola: la del
umbral**, marcada con `+` en el mapa. Se llega a ella caminando desde la vereda
como a cualquier otra celda; el cuerpo del edificio se dibuja pero no es sala, y
desde la calle no hay salida hacia él.

Cada umbral se lleva su propio tramo de vereda: si dos edificios compartieran la
celda de entrada, el segundo quedaría sin acceso.

El `+` solo aparece en los edificios que ocupan varias celdas. En uno de una
sola celda taparía de qué edificio se trata para decir algo que ya se ve.

**Todavía no hay interiores.** El umbral debería tener una salida `entrar` hacia
adentro, pero una salida sin destino no existe en Evennia, y crear ciento
setenta y ocho salas idénticas que digan "está oscuro" solo para que el comando
exista sería peor que no tenerlo. Cuando haya interiores, el `entrar` se agrega
en el constructor, en el umbral.

### La diagonal se camina en diagonal

La Diagonal Sur avanza una celda en cada eje por paso, así que sus tramos se
tocan en la esquina y no de lado: no los une la grilla ortogonal. Se recorre con
`noreste` y `suroeste`. La alternativa —ensancharla en escalera para que la
grilla la uniera— la dibujaba doble.

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
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   Plaza Mayor
▒≡ ≡ ≡ / ┴ ─ ┼▒
▒~ # / , , , │▒   La niebla lo come todo a diez metros. Cae ceniza, mansa,
▒n / ┤ , , , │▒   como nieve sucia.
▒/ # │ @ , , │▒
▒╩ ═ ╬ ═ ═ ═ ╬▒   El centro de Nébrida, y se nota: cuatro hileras de plátanos
▒n # │ A A A │▒   podados en cubo, bancos de hierro fundido y una fuente
▒n # │ A A A │▒   circular en el medio, seca...
▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
Salidas: norte, sur, este y oeste
```

Cada tipo tiene su color: azul el agua, verde la vegetación, gris la trama,
rojo las emergencias, y el jugador en negro sobre amarillo, que es lo único del
mapa con fondo. La paleta está agrupada en familias para que el ojo entienda de
qué se trata antes de identificar el carácter.

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

Ya no se dibujan muros entre celdas. Se probó marcar con un bloque los pares
de salas contiguas sin paso, y el resultado fue un mapa sembrado de manchas
grises alrededor de cada umbral, que es justo donde nunca hay paso lateral. El
edificio se ve macizo porque se dibuja macizo.

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
| `world/mapa/nebrida.py` | **Los textos.** Nombres, descripciones y las conexiones que no son de grilla. |
| `world/mapa/iconos.py` | Tipos de sala a caracteres, y los muros. |
| `world/mapa/render.py` | Dibuja el mapa recorriendo las salidas reales. |
| `world/mapa/constructor.py` | Valida, borra el mundo anterior, construye el nuevo, escribe los dbrefs. |
| `world/batch/nebrida.py` | Punto de entrada del batchprocessor. Tres líneas. |

### Agregar una sala con nombre propio

1. En `ubicaciones.py`, poner el carácter de su tipo en la celda del dibujo.
2. En `nebrida.py`, la entrada en `SALAS`:

```python
SALAS["mi_lugar"] = {
    "nombre": "Mi lugar",
    "exterior": False,        # True antepone la niebla a la descripción
    "desc": "...",
}
```

3. En `ubicaciones.py`, reclamar la celda:

```python
NOMBRADAS["mi_lugar"] = ("nebrida", 42, 22, 0)
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

El constructor etiqueta todo lo que crea con `nebrida` (categoría `mapa`) y
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

La ciudad entera es **un solo plano continuo**. Así se ve completa, sin las
separaciones entre celdas que el juego dibuja para marcar por dónde se pasa:

```
TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT~~~~~TTTTTTTTTTTTTTTTTTTTTTTTTTTTTT
TTTTnnTTTTTTTTTTTTTT│nTTTTTTTTTTTTTTn│TTTTTTT~~~~~TTnnTTTTTTTTTTTTTT%%TTTTTTTTTT
TTn│nnn│TTTTTnnTTTnn│nnnTTTTT║nTTTnnn│nnTTTT~~~~~T│nnn│nTTTTT##TTT%│%%%│TTTTTTTT
nnn│nnn│nTTTnnnn│nnn│nnn│TTTn║nnn│nnn│nnnTTT~~~~~n│nnn/nnTTT###│%%%│%%%│%TTTTTTT
───┼───┼───┬────┼───┼───┼────╬───┼───┼───┬┐~~~~~┌─┼─┬/┼───╦────┼───┼───┤TTTTTTTT
nnn│nnn│nnn│$$$$│XXX│XX.│nnnn║nnn│$$$│nnn├≡≡≡≡≡≡≡n│n/n│nnn║EEE%│%%%│###│$$TTTTTT
nnn│nnn│nnn│$$$$│XXX│XX.│PPnn║nnn│BB$│nnn│~~~~~nnn├/nn│nnn║EEE%│%%%│###│$$TTTTTT
nnn│nnn│nnn│$$$$│XXX│XX.│PPnn║nnn│BB$│nnn│~~~~~nnn/nnn│nnn║EEE%│%%%│###│$TTTTTTT
───┼───┼───┼────┼───┼───┼────╬───┼───┼───~~~~~──┬/┼───┼───╬────┼───┼───┼──TTTTTT
...│nnn│$$$│....│nnn│$$$│....║$$$│...│nnn~~~~~HH/.│nnn│$$$║....│%%%│%%%│TTTTTTTT
...│nnn│$$$│++..│,,n│$$$│....║$$$│...│nn~~~~~│H/H.│nnn│$$$║....│%%%│%%%│%%TTTTTT
...│nnn│$$$│++..│,,n│$$$│....║$$$│...│n~~~~~$├/HH.│nnn│$$$║....│%%%│%%%│%%%TTTTT
───┼───┼───┼────┼───┼───┼────╬───┼───┤~~~~~─┬/┴───┼───┼───╬────┼───┼───┼─TTTTTTT
$$$│###│...│nnnn│nnn│nnn│nnnn║###│...│~~~~~#/┤HHH#│$$$│###║""""│%%%│%%%│%%TTTTTT
$$$│###│...│nnnn│nnn│nnn│nnnn║###│...~~~~~#/#│HHH#│$$$│###║""""│,,,│%%%│TTTTTTTT
───┼───┼───┼────┼───┼───┼────╬───┼─≡≡≡≡≡≡≡/┴─┼────v───┼───╬────┼───┼───┼─TTTTTTT
nnn│nnn│nnn│nnnn│nnn│EEE│nnnn║""n│n~~~~~#/,,,│+++#│PPP│UUU║""""│%%%│%%%│%%%TTTTT
nnn│nnn│,,n│nnnn│nnn│EEE│nnnn║""n│~~~~~n/┤,,,│+++#│PPP│UUU║"*""│%%%│%%%│%%TTTTTT
nnn│nnn│,,n│nnnn│nnn│EEE│nnnn║""n~~~~~n/#│,,,│+++#│PPP│UUU║""""│%%%│%%%│%TTTTTTT
═══╬═══╬═══╬════╬═══╬═══v════╬══~~~~~╔/╩═╬═══╬════╬═══╬═══╬════╬═══╬═══╬═TTTTTTT
...│$$$│nnn│nnnn│###│nnn│nnnn║$~~~~~n/nn#│AAA│LLL$│BBB│&&&║%%%%│RRR│RR.│TTTTTTTT
...│$$$│nnn│$nnn│###│nnn│nnnn~~~~~nn/┤nn#│AAA│LLL$│BBB│&&&║%%%%│RRR│RR.│##TTTTTT
───┼───┼───┼────┼───┼───┼───~~~~~┌┬/┴┼───┼───┼────┼───┼───╬────┼───┼───┼──TTTTTT
nnn│...│nnn│nnnn│$$$│nnn│#~~~~~..├/nn│nn#│###│####│$$$│###║####│%%%│%%%│%TTTTTTT
~~~│...│nnn│nnnn│$$$│nn≡≡≡≡≡≡≡.../nnn│nn#│###│####│$$$│###║####│+++│%%%│%%TTTTTT
~~~~~..│nnn│nnnn│.$$│~~~~~###║../┤nnn│nn#│###│####│$$$│###║####│+++│%%%│TTTTTTTT
~~~~~~~└───┼────┴──~~~~~┌────╬┬/┴┼───┼───┼───┼────┼───┼───╬────┼───┼───┼──TTTTTT
~~~~~~===$$│nnnn~~~~~...│nnnn╠/nn│$$$│nnn│nnn│....│nnn│###║%%%%│%%%│###│$$$TTTTT
~~~~~~~~~~$│nn~~~~~n│,,.│nnnn/"""│$$$│nnn│nnn│....│nnn│###║%%%%│%%%│###│$TTTTTTT
~~~~~~~~~~~~~~~~~nnn│,,.│nnn/╣"""│$$$│nnn│nnn│....│nnn│###║%%%%│%%%│###│$$TTTTTT
~~~~~~~~~~~~~───┬───┼───┼─┬/┴╬───┼───┼───┼───┼────┼───┼───╬────┼───┼───┤TTTTTTTT
~~~~~~~~~~~===%%│###│%%%│#/##║###│%%%│###│%%%│####│%%%│###║####│%%%│###│%TTTTTTT
~~~~~~~~~~~~~~~%│###│%%%├/###║###│%%%│###│%%%│####│%%%│###║####│%%%│###│%%%TTTTT
~~~~~~~~~~~~~~~~└───┼───/┴───╬───┼───┼───┼───┼────┼───┼───╬────┼───┼───┼──TTTTTT
~~~~~~~~~~~~~~~~~%%%│$$$│....║$$$│...│%%%│$$$│....│%%%│$$$║%%%%│$$$│...│%TTTTTTT
~~~~~~~~~~~~~~~===%%│$$$│....║$$$│...│%%%│$$$│....│%%%│$$$║%%%%│$$$│...│%TTTTTTT
~~~~~~~~~~~~~~~~~~~%│$$$│....║$$$│...│%%%│$$$│....│%%%│$$$║%%%%│$$$│...│TTTTTTTT
~~~~~~~~~~~~~~~~~~~─┼───┼────╬───┼───┼───┼───┼────┼───┼───╬────┼───┼───┼──TTTTTT
~~~~~~~~~~~~~~!=====│...│%%%%║nnn│$$$│###│...│%%%%│%%%│nnn║####│...│%%%│%%TTTTTT
~~~~~~~~~~~~~~~~~~~~│...│%%%%║nnn│$$$│###│...│%%%%│%%%│nnn║####│...│%%%│%TTTTTTT
```

`~` el lago y el río · `T` el bosque de las afueras · `≡` los tres puentes ·
`/` la Diagonal Sur · `║ ═ ╬` las avenidas · `│ ─ ┼ ┌ ┘` la trama de calles ·
`n` casas · `#` departamentos · `$` comercios · `%` galpones · `A`
municipalidad · `L` biblioteca · `+` iglesias · `P` comisarías · `B` bomberos ·
`H` hospital · `E` escuelas · `U` hotel · `&` mercado y muelles · `R` la
estación · `X` el cementerio · `"` parques · `,` plazas · `!` el faro · `v` las
bocas de tormenta.

El hospital y las alcantarillas tienen plano propio:

| Plano | Niveles | Qué tiene |
|---|---|---|
| Hospital Municipal | −1 a +3 | admisión, guardia, farmacia, quirófano, morgue, sala de máquinas, dos pisos de internación y el helipuerto |
| Alcantarillas | −1 | pozo de acceso, colector principal, cámara de rejas, oficina de mantenimiento |

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
