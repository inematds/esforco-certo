#!/usr/bin/env bash
# ab.sh — o MESMO trabalho em 2 ou mais combinações de modelo:esforço, pela sua assinatura (claude -p), e um quadro para comparar
# tempo, tokens, custo equivalente e (se você der um teste) se passou.
#
# Uso:
#   ./ab.sh "<tarefa>" [-c modelo:esforço ...] [--dir PASTA] [--editar] [--checar "<comando>"] [--turnos N]
# Exemplos:
#   ./ab.sh "Revise src/ e liste os 5 riscos mais graves, com arquivo e linha"                 # só lê
#   ./ab.sh "Corrija o teste quebrado em tests/" --editar --checar "npm test" -c opus:high -c fable:high
# Padrão: -c opus:high -c fable:medium -c fable:high
#
# Como roda:
#   - sem --editar: cada combinação roda na PASTA só com as ferramentas de leitura (Read, Grep, Glob: não muda nada) e a resposta
#     fica em .ab/resultado-<data>/<combinação>.md (o modo "plan" não serve: nele o Claude Code troca o Haiku pelo Sonnet);
#   - com --editar: cada combinação ganha uma cópia própria (git worktree em .ab/<combinação>), pode editar arquivos (acceptEdits)
#     e, no fim, o script roda o --checar dentro de cada cópia. As cópias ficam para você olhar
#     (apagar: git worktree remove .ab/<combinação>).
#   - ANTHROPIC_API_KEY é retirada do ambiente: o teste usa a ASSINATURA, não a API. Para medir na API de propósito: AB_USAR_API=1.
#   - Cada rodada gasta o seu limite (o Fable gasta mais rápido). Comece com uma tarefa pequena e real.
set -uo pipefail
TAREFA=""; DIR=$PWD; EDITAR=0; CHECAR=""; TURNOS=${AB_TURNOS:-40}; TETO=${AB_TIMEOUT:-1800}; CFGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -c) CFGS+=("$2"); shift 2 ;;
    --dir) DIR=$(realpath "$2"); shift 2 ;;
    --editar) EDITAR=1; shift ;;
    --checar) CHECAR=$2; shift 2 ;;
    --turnos) TURNOS=$2; shift 2 ;;
    -h|--help) sed -n '2,21p' "$0"; exit 0 ;;
    *) [ -z "$TAREFA" ] && TAREFA=$1 || { echo "argumento a mais: $1" >&2; exit 2; }; shift ;;
  esac
done
[ -n "$TAREFA" ] || { echo "uso: ./ab.sh \"<tarefa>\" [-c modelo:esforço ...] (ver --help)" >&2; exit 2; }
[ ${#CFGS[@]} -gt 0 ] || CFGS=(opus:high fable:medium fable:high)
for c in "${CFGS[@]}"; do
  case "${c#*:}" in low|medium|high|xhigh|max) ;; *) echo "esforço inválido em '$c' (use low|medium|high|xhigh|max)" >&2; exit 2 ;; esac
done
command -v claude >/dev/null || { echo "claude (Claude Code) não está no PATH" >&2; exit 2; }
[ "${AB_USAR_API:-0}" = 1 ] || unset ANTHROPIC_API_KEY
if [ $EDITAR = 1 ]; then
  git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "--editar precisa de um repositório git em $DIR" >&2; exit 2; }
  [ -z "$(git -C "$DIR" status --porcelain -- . ':!.ab')" ] || { echo "--editar: deixe o repositório limpo (commit ou stash) antes" >&2; exit 2; }
fi
SAI="$DIR/.ab/resultado-$(date +%Y%m%d-%H%M%S)"; mkdir -p "$SAI"   # tudo do teste fica em .ab/ (ponha .ab/ no .gitignore)
printf '%s\n' "$TAREFA" > "$SAI/TAREFA.txt"
echo "tarefa: $TAREFA"; echo "combinações: ${CFGS[*]} · saída: $SAI"

for c in "${CFGS[@]}"; do
  m=${c%%:*}; e=${c#*:}; nome="${m}-${e}"; onde=$DIR; modo=(--tools "Read Grep Glob")
  if [ $EDITAR = 1 ]; then
    onde="$DIR/.ab/$nome"
    git -C "$DIR" worktree remove --force "$onde" 2>/dev/null; rm -rf "$onde"; git -C "$DIR" worktree prune
    git -C "$DIR" worktree add -q --detach "$onde" HEAD || { echo "worktree falhou ($nome)"; continue; }
    modo=(--permission-mode acceptEdits)
  fi
  echo "→ $nome rodando…"
  ( cd "$onde" && timeout "$TETO" claude -p --model "$m" --effort "$e" --max-turns "$TURNOS" "${modo[@]}" \
      --output-format json -- "$TAREFA" ) > "$SAI/$nome.json" 2> "$SAI/$nome.err"
  rc=$?
  chk="-"
  if [ -n "$CHECAR" ] && [ $EDITAR = 1 ]; then
    ( cd "$onde" && timeout 900 bash -c "$CHECAR" ) > "$SAI/$nome.checar.log" 2>&1 && chk="passou" || chk="falhou"
  fi
  python3 - "$SAI/$nome.json" "$SAI/$nome.md" "$rc" "$chk" "$nome" "$m" >> "$SAI/linhas.tsv" <<'PY'
import json, sys
arq, md, rc, chk, nome, pedido = sys.argv[1:7]
try:
    d = json.load(open(arq))
except Exception:
    print(f"{nome}\tERRO (rc={rc})\t-\t-\t-\t-\t{chk}"); sys.exit()
open(md, 'w').write(d.get('result') or '')
u = d.get('usage') or {}
pens = (u.get('output_tokens_details') or {}).get('thinking_tokens', 0)
modelo = ','.join((d.get('modelUsage') or {}).keys()) or '?'
st = 'erro' if d.get('is_error') else 'ok'
if pedido.lower() not in modelo.lower():
    st = f'⚠ pediu {pedido}, rodou'   # o Claude Code trocou o modelo: a comparação não vale
print(f"{nome}\t{st} ({modelo})\t{d.get('duration_ms', 0)/1000:.0f} s\t{d.get('num_turns', '-')}\t"
      f"{u.get('output_tokens', 0)} (pensando {pens})\tUS$ {d.get('total_cost_usd', 0):.3f}\t{chk}")
PY
  tail -1 "$SAI/linhas.tsv" | cut -f1-2
done

{
  echo "# A/B de esforço — $(date '+%d/%m/%Y %H:%M')"; echo
  echo "Tarefa: $TAREFA"; echo
  echo "| Combinação | Status (modelo) | Tempo | Turnos | Tokens de saída | Custo equivalente* | Teste |"
  echo "|---|---|---|---|---|---|---|"
  sed 's/\t/ | /g; s/^/| /; s/$/ |/' "$SAI/linhas.tsv"
  echo
  echo "\* Custo que o Claude Code calcula pela tabela da API. Na assinatura você não paga isso: paga em limite."
  echo "Leia as respostas ($SAI/*.md) antes de decidir: o mais barato que resolve bem é o seu padrão."
} > "$SAI/RESULTADO.md"
echo; cat "$SAI/RESULTADO.md"
