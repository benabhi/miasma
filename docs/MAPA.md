# El mapa de pruebas: Silent Hill

Escenario de pruebas de Miasma: una reconstrucción de la ciudad de *Silent Hill*
(Konami, 1999). No es contenido definitivo — es un mundo conocido y de tamaño
razonable sobre el que probar cada sistema nuevo a medida que se incorpora.

**104 salas, 238 salidas, 7 distritos.** El juego arranca en el Café 5to2.

---

## Reconstruirlo

Todo el mapa se genera desde datos. Reconstruirlo es un comando, y es
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

## El minimapa

Cada `mirar` sale en dos columnas: el minimapa a la izquierda, el nombre y la
descripción a la derecha, y debajo —a todo el ancho— las salidas, los personajes
y las cosas. Se redibuja solo en cada movimiento, porque lo arma
`Room.return_appearance()` (`typeclasses/rooms.py`).

```
┌─────────┐   Ellroy St. y Midwich St.
│  ˙ ░ ⌂ ▤│
│         │   La niebla lo come todo a diez metros. Cae ceniza, mansa...
│· ˙ ░ ⌂ ▤│
│         │   El paredón perimetral de la Escuela Primaria Midwich corre
│  ˙ ⦿ ▦ ▦│   a lo largo de toda la vereda sur: ladrillo, tres metros...
│         │
└─────────┘
Salidas: oeste, este, norte, sur y escuela
```

`mapa` (alias `map`) muestra el plano entero con una referencia de símbolos.
Acepta un radio: `mapa 5`.

### De dónde salen los iconos

`world/mapa/iconos.py` mapea **tipos** de sala a caracteres. Se trabaja con
tipos y no con caracteres sueltos para poder cambiar la estética del mapa desde
un solo lugar. Hay iconos para calles, avenidas, puentes, callejones,
descampados, comercios, casas, edificios, iglesia, escuela, hospital,
comisaría, hotel, industria, interiores, pasillos, escaleras, sótanos, azoteas,
agua, muelle, faro, alcantarillas y atracciones.

**Todos los caracteres son de ancho simple.** Los emoji (🌲, 🏠) ocupan dos
columnas en la mayoría de las terminales y descuadran la grilla entera, así que
están descartados por más lindos que sean.

### De dónde sale la grilla

`world/mapa/ubicaciones.py` dice dónde cae cada sala. Dos formas:

- **`UBICACIONES`** — salas con celda propia: `(plano, x, y, z, tipo)`. Un
  *plano* es un mapa independiente (`pueblo`, `escuela`, `hospital`, `cloacas`,
  `parque`); dentro de él, `x` crece al este, `y` al norte y `z` es el piso.
- **`ANCLADAS`** — interiores de una sola sala: solo el `tipo`. No ocupan
  celda. Dibujar un mapa de una celda para el interior de un bar no le sirve a
  nadie, así que cuando el jugador está adentro el minimapa muestra la calle de
  la que se entra, con la marca sobre esa celda. El constructor resuelve el
  ancla solo, mirando de dónde se entra.

El pueblo entero —Old Silent Hill, Central y el área turística— es **un solo
plano continuo**, así que caminando de punta a punta se ve cómo encaja la
ciudad. La escuela, el hospital, las alcantarillas y el parque tienen plano
propio.

### Los muros los dicen las salidas, no los datos

`world/mapa/render.py` no dibuja desde `ubicaciones.py`: recorre las **salidas
reales** de cada sala. Entre dos celdas contiguas pone un espacio si hay paso y
un muro si no. Si abrís un pasaje nuevo in-game, el mapa lo refleja sin tocar
ningún dato.

Un muro solo se dibuja entre dos salas que existen y no se comunican. Si de un
lado no hay nada, el mapa termina ahí: el vacío ya dice que no se puede seguir,
y llenarlo de muros lo vuelve ilegible.

### Toda sala necesita un tipo

`Room.at_object_creation()` le pone `tipo_mapa = "interior"` a cualquier sala
que no lo traiga, y el validador del constructor rechaza el build si una sala
no está ni en `UBICACIONES` ni en `ANCLADAS`, si está en las dos, o si dos
salas se pisan en la misma celda. Una sala sin tipo se dibuja como `?`, para
que salte a la vista.

---

## Los archivos

| Archivo | Qué es |
|---|---|
| `world/mapa/silent_hill.py` | **Los datos.** Salas, descripciones y conexiones. Es acá donde se agrega contenido. |
| `world/mapa/ubicaciones.py` | **La geometría.** Dónde cae cada sala y con qué tipo se dibuja. |
| `world/mapa/iconos.py` | El catálogo de tipos a caracteres, y los muros. |
| `world/mapa/render.py` | Dibuja el mapa recorriendo las salidas reales. |
| `world/mapa/constructor.py` | **La lógica.** Valida, borra el mapa anterior, construye el nuevo, escribe los dbrefs. |
| `world/batch/silent_hill.py` | Punto de entrada del batchprocessor. Tres líneas. |

### Agregar una sala

En `silent_hill.py`, una entrada en `SALAS`:

```python
SALAS["int_farmacia"] = {
    "nombre": "Farmacia de Bloch St.",
    "distrito": "old",
    "exterior": False,        # True antepone la niebla a la descripción
    "desc": "...",
}
```

y al menos una tupla en `CONEXIONES`:

```python
CONEXIONES += [
    ("osh_bloch_midwich", "farmacia", "int_farmacia", "fuera"),
]
```

Cada tupla es `(origen, salida_ida, destino, salida_vuelta)`. Si el nombre de la
salida está en `DIRECCIONES` (`norte`, `sur`, `arriba`, `dentro`…) hereda sus
alias automáticamente; si no, es una salida con nombre propio y los alias se
separan con `|`: `"café|cafe|5to2"`. Un `None` como salida de vuelta crea un
pasaje de una sola mano.

### Las validaciones

`constructor.validar()` corre antes de tocar la base y aborta sin construir
nada si encuentra:

- salas inexistentes en una conexión,
- dos salidas con el mismo nombre en la misma sala,
- salas sin ninguna conexión,
- salas inalcanzables caminando desde el punto de partida,
- salas que no están ni en `UBICACIONES` ni en `ANCLADAS`, o que están en las
  dos,
- dos salas peleándose la misma celda del mapa.

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

### Old Silent Hill (29 salas)

Grilla de cuatro por cuatro. Bachman Road es la arteria que atraviesa todo el
pueblo de norte a sur.

```
              Bradbury   Midwich    Levin     Bachman
                 │          │         │          │
  Finney  ───────┼──────────┼─────────┼──────────┼─── (norte: puente roto)
                 │          │         │          │     Café 5to2 · tienda
  Matheson ──────┼──────────┼─────────┼──────────┼───  Queen Burger · casilla
                 │          │         │          │
  Ellroy  ───────┼──────────┼─────────┼──────────┼───  estación de servicio
                 │       ESCUELA      │          │
  Bloch   ───────┼──────────┼─────────┼──────────┴──→ puente levadizo
              Cut-Rite            Iglesia Balkan            │
                                                            ↓
                                                     Central Silent Hill
```

Interiores: Café 5to2 (inicio), tienda de conveniencia, Queen Burger, casa de
Levin Street, casa de K. Gordon, Iglesia Balkan, Cut-Rite Chain Saws, taller de
la estación de servicio, torre de control del puente, cancha de básquet.

### Midwich Elementary School (15 salas)

Planta baja alrededor del patio con la torre del reloj; primer piso con
laboratorio de química, sala de música y biblioteca; sótano con la caldera;
azotea.

### Central Silent Hill (17 salas)

Grilla de cuatro por tres.

```
              Simmons     Sagan     Bachman
                 │          │          │
  Crichton ──────┼──────────┼──────────┼───  comisaría · Green Lion
                 │          │          │
  Koontz  ───────┼──────────┼──────────┼───  Café Sun · HOSPITAL
                 │          │          │
  Munson  ───────┼──────────┼──────────┼───  Town Center
                 │          │          │
  Katz    ───────┴──────────┴──────────┴──→ (sur: área turística)
                        alcantarillas
```

### Hospital Alchemilla (14 salas)

Planta baja completa (recepción, guardia, farmacia, consultorio, dirección,
cocina), subsuelo con el generador, y pisos 2 y 3 por ascensor.

### Las alcantarillas (7 salas)

Unen Katz St. con el área turística. Pozo de acceso, túneles, cruce de
galerías, oficina de mantenimiento, pasarela superior.

### Silent Hill Resort Area (17 salas)

Craig, Weaver, Nathan Ave, Bartlett y Sandford, sobre la costa del lago Toluca.
Annie's Bar, Indian Runner, Motel Haerbey Inn, Pete's Bowl-O-Rama, Lakeview
Hotel, el muelle y el faro.

### Lakeside Amusement Park (5 salas)

Explanada, heladería, vuelta al mundo, montaña rusa y calesita.

---

## Deuda conocida

- Las descripciones son estáticas. Cuando exista el sistema de luz y clima
  (fase 3 de `DISENO.md`), las salas de exterior deberían describir distinto de
  día y de noche, y la constante `NIEBLA` debería salir de ahí.
- No hay puertas ni cerraduras: todas las salidas están abiertas. Las que en el
  juego original están cerradas con llave (la azotea de la escuela, la reja de
  las alcantarillas, Indian Runner) están descritas como cerradas pero se
  cruzan igual.
- No hay objetos ni NPCs. El mapa es geografía pura.
- El minimapa no marca las escaleras: si una sala tiene salidas hacia otro
  nivel, hay que entrar para enterarse. `mapa` sí dice en qué nivel estás y
  cuántos tiene el plano.
- El interior de la escuela y del hospital está resumido: hay una sala por zona
  significativa, no una por aula o consultorio.
