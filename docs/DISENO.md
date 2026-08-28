# Miasma — documento de diseño

Estado: **esqueleto inicial**. Fija el rumbo y el vocabulario; no es un
contrato. Todo lo de acá se discute antes de implementarse.

---

## 1. Qué es

Un MUD de supervivencia hardcore en un mundo post-Brote. La referencia es
*Cataclysm: Dark Days Ahead*: profundidad de simulación por encima de la
progresión, crafteo desde chatarra, y una muerte que borra el personaje.

Lo que **no** es: un hack-and-slash de zombis, ni un MUD de niveles con
temática apocalíptica encima.

## 2. Pilares

1. **La muerte es final.** Permadeath real. La cuenta sobrevive; el personaje
   no. Lo que dejás atrás queda en el mundo para el que lo encuentre.
2. **El cuerpo es el recurso.** No hay barra de vida abstracta: hay partes del
   cuerpo, heridas que se infectan, hambre, sed, temperatura, sueño, dolor y
   toxinas. La mayoría de las muertes no las causa un mordisco, sino lo que
   viene después del mordisco.
3. **Todo es material.** Nada aparece de la nada. Un cuchillo es acero, mango y
   filo; se desafila, se rompe, se puede fabricar con una lata y cinta.
4. **La mutación es una decisión con costo.** No es progresión: es cambiar algo
   que te sirve por algo que te sirve de otra manera. Rama vegetal, insectoide,
   feral, quitinosa... cada una da y saca.
5. **El mundo no espera.** Ciclo día/noche real, clima, cadáveres que se
   pudren, hordas que se mueven. El jugador desconectado no congela el mundo.

## 3. Sistemas, en orden de construcción

Cada fase debe quedar jugable antes de empezar la siguiente.

### Fase 0 — Cimientos *(hecho)*
- Entorno dockerizado, Evennia 6.1.0, Postgres, gamedir montado.
- Escenario de pruebas: Nébrida, una ciudad de 2452 salas generada desde
  datos y reconstruible con un comando (ver `MAPA.md`).
- Juego en español: comandos de jugador traducidos y catálogo del motor al
  100% (ver `TRADUCCION.md`).

### Fase 1 — El cuerpo
- Modelo de partes del cuerpo y heridas (sangrado, fractura, infección).
- Necesidades: hambre, sed, temperatura, fatiga.
- Muerte y permadeath: archivado del personaje y liberación del cupo.
- Creación de personaje: origen, oficio, rasgos y taras.

### Fase 2 — Materia
- Objetos con material, peso, volumen, durabilidad y estado.
- Inventario por volumen y peso, no por cantidad de slots.
- Contenedores, ropa por capas y cobertura por parte del cuerpo.
- Crafteo: recetas, herramientas requeridas, tiempo, fallo parcial.

### Fase 3 — El mundo
- Salas exteriores/interiores, luz, clima y temperatura ambiente.
- Ciclo día/noche atado a `TIME_FACTOR` (1 día = 6 h reales).
- Saqueo: generación de loot por tipo de edificio, agotable.

### Fase 4 — Lo que camina
- IA de zombis: percepción por sonido, olor y vista; hordas.
- Variantes y mutaciones de los infectados.
- Combate: alcance, partes del cuerpo, resistencia, ruido.

### Fase 5 — Mutación del jugador
- Toxinas, mutágenos y ramas mutagénicas.
- Umbral: el punto donde dejás de ser del todo humano.

### Fase 6 — Otros supervivientes
- Refugios y construcción.
- NPCs, facciones, comercio.
- PvP con consecuencias y reputación.

## 4. Decisiones tomadas

| Decisión | Valor | Por qué |
|---|---|---|
| Framework | Evennia 6.1.0 | Python, typeclasses persistentes, batteries included |
| Base de datos | PostgreSQL 17 | El modelo de atributos de Evennia castiga a sqlite bajo carga |
| Idioma | Español (`LANGUAGE_CODE = "es"`) | Público objetivo; hay hueco en MUDs hispanos |
| Reloj | `TIME_FACTOR = 4.0` | 1 día de juego cada 6 h reales |
| Época | 1 abr 2033, 06:00 UTC | Fecha canónica, semanas después del Brote |
| Personajes por cuenta | 1 | Refuerza el peso de la permadeath |
| Chargen | Pospuesto | Hoy se entra directo: al crear la cuenta se crea el personaje. Vuelve en la fase 1, cuando haya algo que elegir |

## 5. Preguntas abiertas

- ¿Mapa a mano o generación procedural de la ciudad?
- ¿Escala del mundo: un barrio, una ciudad, una región?
- ¿La permadeath borra el personaje o lo deja como cadáver saqueable?
- ¿Cuánto PvP: libre, por zonas, o consentido?
- ¿El crafteo usa recetas fijas o combinación libre de materiales?
