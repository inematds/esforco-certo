# esforço certo

[![esforço certo](guia/assets/banner.jpg)](https://inematds.github.io/esforco-certo/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

O esforço certo é um kit gratuito para quem usa o Claude Code em projetos e robôs. Ele lê as configurações, os agentes e os scripts do seu projeto e mostra em que modelo (Fable, Opus, Sonnet, Haiku) e em que esforço cada coisa roda — esforço é quanto o modelo pensa antes de responder, de `low` a `max`. Ele aponta o que está caro sem precisar, traz uma regra pronta para colar no seu CLAUDE.md e um teste que roda o mesmo trabalho em dois esforços, pela sua assinatura, para você comparar. Precisa de Python 3 e, para o teste, do Claude Code; a auditoria não usa internet nem API.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/esforco-certo/guia/**

## Por quê

Na página de lançamento do Claude Fable 5.2 (09/11/2026), a Anthropic recomenda começar no **Opus 5.5** para a maioria do
código e do trabalho do dia a dia, e subir para o Fable só no trabalho mais difícil. No gráfico de custo por tarefa do
teste FrontierCode 2.0 da mesma página:

| Combinação | Nota | Custo por tarefa (lido no gráfico) |
|---|---|---|
| Fable 5.2 · high | 45,3% | ~US$ 7 |
| Opus 5.5 · melhor | 45,5% | ~US$ 13 |
| Fable 5.2 · xhigh | 49,1% | ~US$ 15 |
| Fable 5.2 · max | ~45,7% | ~US$ 45 |

O Max fez menos que o Xhigh e custou cerca de 3×. Em outro teste (desenho de hardware) o melhor veio no Max — por isso a
regra é **Max não é padrão; meça**. E a tabela de notas é sempre no esforço mais alto, enquanto o Claude Code vem no
medium por padrão.

## Começo rápido

```bash
git clone https://github.com/inematds/esforco-certo.git
cd esforco-certo
python3 auditar.py ~/meu-projeto --home          # quem roda em qual modelo/esforço, e o que está caro
cat politica/CLAUDE-esforco.md >> ~/meu-projeto/CLAUDE.md
./ab.sh "Revise src/ e liste os 5 riscos mais graves" --dir ~/meu-projeto   # mesmo trabalho, 3 combinações
```

## Conteúdo

| Arquivo | O que faz |
|---|---|
| `auditar.py` | Lê `.claude/settings*.json` (`model`, `effortLevel`, `modelSettings.<modelo>.effortLevel`), agentes, skills, comandos, scripts, timers e código que chama a API. Alertas: `MAX`, `PADRAO_ALTO`, `FABLE_PADRAO`. Opções: `--home`, `--json`, `--estrito` (CI), `--anonimo`, `--docs`. |
| `ab.sh` | Roda o mesmo pedido com `claude -p` em 2+ combinações `modelo:esforço` (padrão `opus:high fable:medium fable:high`). Só leitura por padrão; `--editar` usa uma git worktree do último commit por combinação (commite antes; ela vem sem `node_modules`/`.venv`) e `--checar "<cmd>"` roda o seu teste — instale as dependências nele, ex.: `--checar "npm ci && npm test"`. Quadro com tempo, tokens, custo equivalente e o modelo que rodou de verdade. Usa a assinatura (tira `ANTHROPIC_API_KEY` do ambiente). |
| `politica/CLAUDE-esforco.md` | Bloco pronto para o CLAUDE.md/AGENTS.md. |
| `agentes/` | `dia-a-dia` (Opus, medium), `trabalho-longo` (Fable, high), `mecanico` (Haiku, low). |
| `resets.md` | Roteiro para gastar os resets do Fable (promoção até 16/11/2026) num trabalho longo. |
| `exemplos/` | Relatório do projeto de teste e o resumo de uma máquina de produção. |
| `tests/` | 18 testes sem rede: `python3 -m unittest discover tests`. |

## O processo, do início ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar o kit | `git clone https://github.com/inematds/esforco-certo.git` | 🧠 você |
| 2 | Auditar o projeto | `python3 auditar.py <pasta> --home` | ⚙️ script |
| 3 | Decidir o padrão com os alertas | ler o relatório; mudar `model`/`effortLevel` à mão | 🧠 você |
| 4 | Colar a regra e os agentes | `cat politica/CLAUDE-esforco.md >> CLAUDE.md` · `cp agentes/*.md .claude/agents/` + `git commit` | 🧠 você |
| 5 | Medir no seu trabalho | `./ab.sh "<tarefa>" --dir <pasta> [--editar --checar "<teste>"]` | 🤖 `claude -p` |
| 6 | Travar no CI | `cp auditar.py <projeto>/tools/` · no CI: `python3 tools/auditar.py . --estrito` | ⚙️ script |
| 7 | Gastar os resets num trabalho longo | seguir `resets.md` | 🧠 você + 🤖 |

## Limites

- A auditoria acha o que está escrito; não sabe o que um script decide em tempo de execução (modelo vindo de variável aparece como `variavel`).
- O custo do `ab.sh` é o que o Claude Code calcula pela tabela da API; na assinatura você paga em limite, não em dólar.
- Números do Fable 5.2 e do Opus 5.5: testes da própria Anthropic, lidos em 09/11/2026.

Projetos e cursos gratuitos: https://inema.club
