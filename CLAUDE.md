# CLAUDE.md — esforco-certo

Kit para decidir modelo e esforço no Claude Code: `auditar.py` (stdlib, só leitura), `ab.sh` (claude -p pela assinatura),
`politica/`, `agentes/`, `resets.md`, guia em `guia/` (PT) + `guia/en/` + `guia/es/`.

## Regras do projeto
- Só leitura: o auditor nunca muda arquivo; sugestões são texto.
- `ab.sh` sempre pela assinatura: tira `ANTHROPIC_API_KEY` do ambiente (só `AB_USAR_API=1` mantém).
- Números do Fable 5.2 / Opus 5.5: só os da página da Anthropic de 09/11/2026 (`anthropic.com/claude-fable-and-mythos-5-2`). Não citar vídeo, canal ou autor de referência.
- Exemplos publicados: `--anonimo`, sem nomes de pastas privadas; conferir com grep antes do commit.
- Autor dos commits: `inematds <inematds@gmail.com>`.
- Testes sem rede: `python3 -m unittest discover tests`.

## Self-learning

When I correct you, or you catch yourself making a mistake: before continuing, add the lesson as a one-line rule at the TOP of the Lessons list below, so it never happens again.

## Lessons
- `claude -p --permission-mode plan` troca o Haiku pelo Sonnet: modo só-leitura do ab.sh = `--tools "Read Grep Glob"`, e o quadro compara o modelo pedido com o `modelUsage` (09/11/2026).
- `modelSettings.<modelo>.effortLevel` repete chave e valor no settings: cada achado pega a próxima linha livre, e esforço por modelo não é "modelo padrão" (09/11/2026).
- `log "... claude -p ..."`/`echo` citam o comando sem rodar: linha que começa com echo/log/print não conta (09/11/2026).
