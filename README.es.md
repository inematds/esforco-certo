# esfuerzo justo

[![esfuerzo justo](guia/assets/banner-es.jpg)](https://inematds.github.io/esforco-certo/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Esfuerzo justo es un kit gratuito para quienes usan Claude Code en proyectos y robots. Lee las configuraciones, los agentes y los scripts de tu proyecto y muestra en qué modelo (Fable, Opus, Sonnet, Haiku) y con qué esfuerzo se ejecuta cada cosa: el esfuerzo indica cuánto piensa el modelo antes de responder, de `low` a `max`. Señala qué está costando más de lo necesario, incluye una regla lista para pegar en tu CLAUDE.md y una prueba que ejecuta el mismo trabajo con dos niveles de esfuerzo, usando tu suscripción, para que puedas compararlos. Necesitas Python 3 y, para la prueba, Claude Code; la auditoría no usa internet ni API.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/esforco-certo/guia/es/**

## Por qué

En la página de lanzamiento de Claude Fable 5.2 (09/11/2026), Anthropic recomienda empezar con **Opus 5.5** para la mayoría del código y del trabajo cotidiano, y pasar a Fable solo para las tareas más difíciles. En el gráfico de costo por tarea de la prueba FrontierCode 2.0 de esa misma página:

| Combinación | Puntuación | Costo por tarea (leído en el gráfico) |
|---|---|---|
| Fable 5.2 · high | 45,3% | ~US$ 7 |
| Opus 5.5 · mejor | 45,5% | ~US$ 13 |
| Fable 5.2 · xhigh | 49,1% | ~US$ 15 |
| Fable 5.2 · max | ~45,7% | ~US$ 45 |

Max rindió menos que Xhigh y costó cerca de 3×. En otra prueba (diseño de hardware), el mejor resultado se obtuvo con Max; por eso, la regla es **Max no es el valor predeterminado; mide**. Además, la tabla de puntuaciones siempre usa el esfuerzo más alto, mientras que Claude Code viene configurado en medium de forma predeterminada.

## Inicio rápido

```bash
git clone https://github.com/inematds/esforco-certo.git
cd esforco-certo
python3 auditar.py ~/meu-projeto --home          # quién ejecuta qué modelo/esfuerzo, y qué está costando más de lo necesario
cat politica/CLAUDE-esforco.md >> ~/meu-projeto/CLAUDE.md
./ab.sh "Revise src/ e liste os 5 riscos mais graves" --dir ~/meu-projeto   # mismo trabajo, 3 combinaciones
```

## Contenido

| Archivo | Qué hace |
|---|---|
| `auditar.py` | Lee `.claude/settings*.json` (`model`, `effortLevel`, `modelSettings.<modelo>.effortLevel`), agentes, skills, comandos, scripts, timers y código que llama a la API. Alertas: `MAX`, `PADRAO_ALTO`, `FABLE_PADRAO`. Opciones: `--home`, `--json`, `--estrito` (CI), `--anonimo`, `--docs`. |
| `ab.sh` | Ejecuta el mismo pedido con `claude -p` en 2 o más combinaciones `modelo:esfuerzo` (predeterminadas: `opus:high fable:medium fable:high`). Solo lectura de forma predeterminada; `--editar` usa un git worktree del último commit por combinación (haz commit antes; viene sin `node_modules`/`.venv`) y `--checar "<cmd>"` ejecuta tu prueba — instala las dependencias en él, p. ej. `--checar "npm ci && npm test"`. Muestra tiempo, tokens, costo equivalente y el modelo que realmente se ejecutó. Usa tu suscripción (quita `ANTHROPIC_API_KEY` del entorno). |
| `politica/CLAUDE-esforco.md` | Bloque listo para CLAUDE.md/AGENTS.md. |
| `agentes/` | `dia-a-dia` (Opus, medium), `trabalho-longo` (Fable, high), `mecanico` (Haiku, low). |
| `resets.md` | Guía para gastar los resets de Fable (promoción hasta el 16/11/2026) en un trabajo largo. |
| `exemplos/` | Informe del proyecto de prueba y resumen de una máquina de producción. |
| `tests/` | 16 pruebas sin red: `python3 -m unittest discover tests`. |

## El proceso, de principio a fin

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Descargar el kit | `git clone https://github.com/inematds/esforco-certo.git` | 🧠 tú |
| 2 | Auditar el proyecto | `python3 auditar.py <pasta> --home` | ⚙️ script |
| 3 | Decidir el valor predeterminado a partir de las alertas | leer el informe; cambiar `model`/`effortLevel` manualmente | 🧠 tú |
| 4 | Pegar la regla y los agentes | `cat politica/CLAUDE-esforco.md >> CLAUDE.md` · `cp agentes/*.md .claude/agents/` + `git commit` | 🧠 tú |
| 5 | Medir en tu trabajo | `./ab.sh "<tarea>" --dir <carpeta> [--editar --checar "<prueba>"]` | 🤖 `claude -p` |
| 6 | Bloquear en CI | `cp auditar.py <proyecto>/tools/` · en CI: `python3 tools/auditar.py . --estrito` | ⚙️ script |
| 7 | Gastar los resets en un trabajo largo | seguir `resets.md` | 🧠 tú + 🤖 |

## Límites

- La auditoría detecta lo que está escrito; no sabe qué decide un script en tiempo de ejecución (el modelo que viene de una variable aparece como `variavel`).
- El costo de `ab.sh` es el que Claude Code calcula según la tabla de la API; con la suscripción pagas con un límite, no en dólares.
- Cifras de Fable 5.2 y Opus 5.5: pruebas de la propia Anthropic, consultadas el 09/11/2026.

Proyectos y cursos gratuitos: https://inema.club