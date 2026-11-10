#!/usr/bin/env bash
claude -p --model opus --effort high -- "revise o PR"
claude -p \
  --model fable \
  --effort max "migre o serviço"
claude -p "resuma o log"
claude -p --model "$MODELO" --effort "$ESFORCO" "variável"
codex exec -m gpt-6-astra -c model_reasoning_effort=high -
# claude -p --model fable --effort max  (comentário: não conta)
log "fase: claude -p ($MODELO)"
echo "rode: claude -p --model fable --effort max"
claude -p --model opus "sem esforço explícito"
echo "resuma o log" | claude -p --model fable --effort max
printf '%s' "$P" | codex exec -m gpt-6-astra -
