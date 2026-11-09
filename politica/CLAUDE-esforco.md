## Modelo e esforço (cole este bloco no seu CLAUDE.md ou AGENTS.md)

<!-- esforco-certo 1.0 · base: página de lançamento do Claude Fable 5.2, Anthropic, 09/11/2026 -->

- **Padrão do dia a dia: Opus 5.5, esforço `medium`** (o padrão do Claude Code). Código comum, revisão, texto, pesquisa.
- **Subir para o Fable 5.2, esforço `high`**, só no trabalho longo e difícil: migração, auditoria de um sistema inteiro,
  agentes rodando por horas, problema que o Opus já tentou e não resolveu. No teste de código FrontierCode, o Fable no
  `high` empatou com o melhor do Opus por cerca de metade do custo por tarefa.
- **`xhigh` é exceção**: só quando a nota importa e você mediu (ex.: `ab.sh` com e sem `xhigh`).
- **`max` nunca é padrão.** No FrontierCode o `max` fez menos que o `xhigh` e custou ~3× mais. Em outro teste
  (desenho de hardware) o melhor veio no `max`: use só com um teste que prove o ganho no SEU trabalho.
- **Tarefa mecânica** (renomear, extrair, formatar, buscar padrão): Haiku 5.5 ou Sonnet 5.5, esforço `low`.
- **Robôs e timers** (`claude -p` em script): sempre `--model` e `--effort` explícitos; sem isso o script herda o padrão da
  conta e muda de custo sem você ver.
- **Placar não é o que você roda:** as notas publicadas são no esforço mais alto disponível; antes de trocar de modelo
  por causa de uma tabela, rode o mesmo trabalho nos dois (`ab.sh`) e compare resultado, tempo e limite gasto.
- Conferir de tempos em tempos: `python3 tools/auditar.py . --home` (lista quem fixa modelo/esforço e o que está caro sem
  precisar; o `auditar.py` vem do kit esforco-certo — copie para `tools/` ou rode da pasta do kit).
