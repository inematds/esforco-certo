# Plano dos resets do Fable (promoção de lançamento, até 16/11/2026)

A Anthropic deu de 1 a 3 resets do Fable 5.2 conforme o tempo de assinatura, e no Pro / Team padrão o Fable entra em
até metade do limite da semana. O conselho: **não gaste reset no dia a dia** (para isso, Opus 5.5). Gaste no
**trabalho longo que você vem adiando**.

## 1. Escolha UM trabalho (10 min)
- [ ] Algo que leva horas e que você adia: migração (linguagem, framework, banco), auditoria do sistema inteiro,
      limpeza de dívida técnica grande, testes para um módulo sem testes.
- [ ] Tem um jeito de saber se ficou pronto: comando → saída esperada (ex.: `npm test` verde, `pytest` sem falha,
      `auditar.py --estrito` com código 0).

## 2. Prepare antes de gastar o reset (30 min, no Opus)
- [ ] Repositório limpo e num branch novo (ou `git worktree`), para poder jogar fora.
- [ ] `CLAUDE.md` com o objetivo, o critério de pronto e o que não fazer (cole o `politica/CLAUDE-esforco.md`).
- [ ] Os testes que provam o pronto já existem e rodam (escreva no Opus se faltar).

## 3. Rode no Fable, esforço high
```bash
claude --model fable --effort high
# ou, sem parar, com o agente pronto deste kit:
cp agentes/trabalho-longo.md .claude/agents/
```
- [ ] Acompanhe o uso em Configurações → Uso. Quando chegar perto do limite do Fable, use o reset.
- [ ] Não troque para `max` no meio. Se travar, peça o diagnóstico e decida você.

## 4. Feche (no Opus)
- [ ] Rode o critério de pronto. Revise o diff. Só então faça merge.
- [ ] Anote no `CLAUDE.md` o que aprendeu (o que o Fable fez bem, onde travou) para a próxima vez.
