# Comparar dos modelos sin engañarse: ¿capacidad, interpretación o esfuerzo?

Una comparación de «mismo prompt, ¿cuál quedó más bonito?» mezcla tres cosas:

| Factor | La pregunta | Cómo se manifiesta |
|---|---|---|
| **Capacidad** | ¿El modelo ve por sí solo cómo mejorar el proyecto, sin recibir instrucciones? | Detalles que nadie pidió y que tienen sentido |
| **Interpretación** | ¿Entendió mejor el objetivo y tomó la decisión correcta? | Cumple lo que se pidió, incluso lo que estaba implícito |
| **Esfuerzo** | ¿Dedicó más tiempo, razonamiento, herramientas y dinero? | Trabajó más, llamó a más herramientas, costó más |

Si un modelo trabaja mucho más tiempo y gasta mucho más, parte de la diferencia puede deberse solo a **más esfuerzo**, no a más inteligencia.  
Y «fue más allá de lo pedido» (animación, imagen, personaje) impresiona a quien evalúa, pero no es lo mismo que **resolver mejor el pedido**: en un juego, que se vea más bonito y se juegue peor es resolverlo peor.

## Los tres experimentos

Haz los tres antes de concluir qué modelo es «mejor» para ti. Cada uno responde a una pregunta distinta.

### 1. Mismo pedido, mismo presupuesto

Mismo prompt, mismo límite de turnos y de tiempo, mismas herramientas.  
**Responde:** quién ofrece más calidad con los mismos recursos.

```bash
./ab.sh "<tarefa>" --dir <projeto> --turnos 30 -c opus:high -c fable:high
```

`--turnos` se aplica por igual a todas las combinaciones; la tabla muestra el tiempo, los tokens y el costo equivalente de cada una.

### 2. Mismo pedido, máximo esfuerzo

Mismo prompt inicial, cada modelo con el nivel de esfuerzo en el que rinde mejor, sin un límite estricto. Registra todo el costo.  
**Responde:** cuál produce el mejor resultado final y cuánto cuesta llegar a él.

```bash
./ab.sh "<tarefa>" --dir <projeto> -c opus:xhigh -c fable:xhigh
```

### 3. Mismo resultado esperado

Ambos reciben los mismos criterios objetivos (¿funciona?, ¿pasa las pruebas?, ¿cumple cada requisito?) y trabajan hasta alcanzar el estándar. Mide **cuántas rondas, correcciones y minutos tuyos** hicieron falta.  
**Responde:** cuánto cuesta, en total, convertir la especificación en un producto listo.

```bash
./ab.sh "<tarefa com os critérios escritos>" --dir <projeto> --editar --checar "npm ci && npm test" -c opus:high -c fable:high
```

`ab.sh` ejecuta una ronda por combinación. Si la prueba no pasa, pide la corrección y vuelve a ejecutarla; anota cada ronda en la ficha de abajo.

## Ficha de evaluación (cópiala en tu proyecto)

Antes de ver el resultado, escribe los criterios. Después, pon una nota separando **lo que se pidió** de **lo que se añadió**.

| Criterio | Peso | Modelo A | Modelo B |
|---|---|---|---|
| Cumple cada requisito solicitado (lista) | 40% | | |
| Funciona / pasa las pruebas | 30% | | |
| Calidad de lo solicitado | 15% | | |
| Extras útiles (no solicitados) | 5% | | |
| Errores o regresiones | −10% cada uno | | |
| **Tiempo** (min) · **costo** · **rondas** · **tus minutos de corrección** | — | | |

Reglas de la ficha:

- **Un extra no solicitado vale poco** si no se cumplió el pedido. Algo bonito que no funciona no gana.
- **Mismo evaluador, sin saber cuál es cuál** (cambia los nombres de las carpetas por A y B antes de revisarlas).
- **Costo total = modelo + tu tiempo.** Una hora tuya corrigiendo pesa más que unos pocos dólares en tokens.

## Lo que un único intento NO demuestra

Una ronda de «mismo prompt, ¿cuál quedó más bonito?» no demuestra que un modelo:

- interprete mejor todos los requisitos;
- escriba mejor código;
- cometa menos errores;
- necesite menos intervenciones;
- ofrezca más productividad por dólar;
- haya ganado por capacidad y no por haber trabajado más.

La pregunta correcta no es qué modelo hace la pantalla más bonita en un intento, sino **cuál convierte una especificación en un producto excelente y funcional con el menor costo total**.
