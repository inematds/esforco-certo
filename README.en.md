# right effort

[![right effort](guia/assets/banner-en.jpg)](https://inematds.github.io/esforco-certo/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

Right effort is a free toolkit for people who use Claude Code in projects and bots. It reads your project’s settings, agents, and scripts and shows which model (Fable, Opus, Sonnet, Haiku) and effort each thing runs at — effort is how much the model thinks before answering, from `low` to `max`. It points out what’s unnecessarily expensive, provides a ready-to-paste rule for your CLAUDE.md, and includes a test that runs the same task at two effort levels using your subscription so you can compare. It requires Python 3 and, for the test, Claude Code; the audit uses neither the internet nor an API.

## 📖 User guide

Complete guide (landing page + walkthrough): **https://inematds.github.io/esforco-certo/guia/en/**

## Why

On the Claude Fable 5.2 launch page (11/09/2026), Anthropic recommends starting with **Opus 5.5** for most coding and everyday work, and moving up to Fable only for the hardest tasks. In the cost-per-task chart from the FrontierCode 2.0 test on the same page:

| Combination | Score | Cost per task (read from chart) |
|---|---|---|
| Fable 5.2 · high | 45.3% | ~US$ 7 |
| Opus 5.5 · best | 45.5% | ~US$ 13 |
| Fable 5.2 · xhigh | 49.1% | ~US$ 15 |
| Fable 5.2 · max | ~45.7% | ~US$ 45 |

Max scored lower than Xhigh and cost about 3× as much. In another test (hardware design), the best result came at Max — so the rule is **Max is not the default; measure**. And the scores table always uses the highest effort, while Claude Code defaults to medium.

## Quick start

```bash
git clone https://github.com/inematds/esforco-certo.git
cd esforco-certo
python3 auditar.py ~/meu-projeto --home          # who runs on which model/effort, and what is expensive
cat politica/CLAUDE-esforco.md >> ~/meu-projeto/CLAUDE.md
./ab.sh "Review src/ and list the 5 most serious risks" --dir ~/meu-projeto   # same task, 3 combinations
```

## Contents

| File | What it does |
|---|---|
| `auditar.py` | Reads `.claude/settings*.json` (`model`, `effortLevel`, `modelSettings.<modelo>.effortLevel`), agents, skills, commands, scripts, timers, and code that calls the API. Alerts: `MAX`, `PADRAO_ALTO`, `FABLE_PADRAO`. Options: `--home`, `--json`, `--estrito` (CI), `--anonimo`, `--docs`. |
| `ab.sh` | Runs the same prompt with `claude -p` across 2+ `model:effort` combinations (default `opus:high fable:medium fable:high`). Read-only by default; `--editar` uses one git worktree of the last commit per combination (commit first; it comes without `node_modules`/`.venv`), and `--checar "<cmd>"` runs your test — install dependencies in it, e.g. `--checar "npm ci && npm test"`. Shows time, tokens, equivalent cost, and the model that actually ran. Uses your subscription (removes `ANTHROPIC_API_KEY` from the environment). |
| `politica/CLAUDE-esforco.md` | Ready-to-use block for CLAUDE.md/AGENTS.md. |
| `politica/comparar-modelos.en.md` | Protocol to compare two models without fooling yourself: separates capability, interpretation and effort in 3 experiments (same budget, best effort, same result) + a blind evaluation form. |
| `agentes/` | `dia-a-dia` (Opus, medium), `trabalho-longo` (Fable, high), `mecanico` (Haiku, low). |
| `resets.md` | Guide to using Fable resets (promotion through 16/11/2026) on a long-running task. |
| `exemplos/` | Report from the test project and a summary of a production machine. |
| `tests/` | 19 offline tests: `python3 -m unittest discover tests`. |

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Download the toolkit | `git clone https://github.com/inematds/esforco-certo.git` | 🧠 you |
| 2 | Audit the project | `python3 auditar.py <pasta> --home` | ⚙️ script |
| 3 | Choose the default based on the alerts | read the report; manually change `model`/`effortLevel` | 🧠 you |
| 4 | Add the rule and agents | `cat politica/CLAUDE-esforco.md >> CLAUDE.md` · `cp agentes/*.md .claude/agents/` + `git commit` | 🧠 you |
| 5 | Measure on your own work (to compare models: the 3 experiments in `politica/comparar-modelos.en.md`) | `./ab.sh "<task>" --dir <folder> [--editar --checar "<test>"]` | 🤖 `claude -p` |
| 6 | Enforce in CI | `cp auditar.py <project>/tools/` · in CI: `python3 tools/auditar.py . --estrito` | ⚙️ script |
| 7 | Use the resets on a long-running task | follow `resets.md` | 🧠 you + 🤖 |

## Limitations

- The audit finds what is written down; it cannot tell what a script decides at runtime (a model coming from a variable appears as `variavel`).
- The cost shown by `ab.sh` is what Claude Code calculates using the API price table; with a subscription, you pay against a limit, not in dollars.
- Fable 5.2 and Opus 5.5 figures: Anthropic’s own tests, reviewed on 11/09/2026.

Free projects and courses: https://inema.club