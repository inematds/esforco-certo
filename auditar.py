#!/usr/bin/env python3
"""auditar.py — mostra em que MODELO e em que ESFORÇO o seu projeto roda o Claude (e o Codex).

Lê, sem rede e sem mudar nada:
  - .claude/settings*.json            → "model", "effortLevel", env ANTHROPIC_MODEL
  - .claude/agents/*.md, skills/*/SKILL.md → frontmatter "model:" e "effort:"
  - scripts, timers, CI (.sh .py .js .ts .service .yml …) → "claude … --model X --effort Y", "codex exec -m X"
  - código que chama a API            → ids "claude-fable-5-2", "claude-opus-5-5"… e effort na mesma linha
e aponta o que custa caro sem precisar: Max fixo, Xhigh/Max como padrão global, Fable como padrão.

Uso:
  python3 auditar.py [PASTA ...] [--home] [--json] [--estrito] [--anonimo] [--docs]
    --home      também lê ~/.claude (settings, agents, skills) e ~/.config/systemd/user
    --json      saída em JSON (para CI ou outro script)
    --estrito   sai com código 1 se houver alerta (Max fixo, padrão alto, Fable padrão) — use no CI
    --anonimo   troca o caminho da sua pasta pessoal por ~ (para publicar o relatório)
    --docs      inclui .md/.html na busca de comandos (por padrão, ficam fora: exemplo em README não roda)

Regra por trás dos alertas (página de lançamento do Fable 5.2, Anthropic, 09/11/2026):
  - comece no Opus 5.5 e suba para o Fable no trabalho mais difícil;
  - no FrontierCode 2.0 o esforço Max fez MENOS que o Xhigh e custou ~3x mais (em outro teste, BenchCAD, o melhor veio no Max):
    Max não é padrão — é exceção medida;
  - o Claude Code vem no esforço médio por padrão; a tabela de notas é sempre no esforço mais alto.
"""
import json, os, re, sys
from datetime import date
from pathlib import Path

VERSAO = '1.0.1'
MARCA = 'auditar.py — mostra em que MODELO'
IGNORAR_DIR = {'.git', 'node_modules', '.venv', 'venv', 'env', '__pycache__', 'dist', 'build', '.next', '.cache',
               'site-packages', '.mypy_cache', '.pytest_cache', '.tox', 'target', 'vendor', '.ab'}
EXT_SCRIPT = {'.sh', '.bash', '.zsh', '.py', '.js', '.mjs', '.cjs', '.ts', '.service', '.timer', '.yml', '.yaml',
              '.toml', '.env', '.conf', '.ini', '.ps1', '.bat', '.cmd'}
NOMES_SCRIPT = {'Makefile', 'Dockerfile', 'crontab', 'Procfile', 'justfile'}
EXT_DOCS = {'.md', '.html', '.txt'}
MAX_BYTES = 1_000_000
ESFORCOS = ['low', 'medium', 'high', 'xhigh', 'max']

RE_CLAUDE = re.compile(r'(?<![\w/.-])claude(?:\s|$)')
RE_CODEX = re.compile(r'(?<![\w/.-])codex\s+exec\b')
RE_MODEL_FLAG = re.compile(r'--model(?:=|\s+)(["\']?)([^\s"\']+)\1')
RE_EFFORT_FLAG = re.compile(r'--effort(?:=|\s+)(["\']?)([^\s"\']+)\1')
RE_CODEX_M = re.compile(r'(?:\s-m|--model)(?:=|\s+)(["\']?)([^\s"\']+)\1')
RE_CODEX_EF = re.compile(r'model_reasoning_effort\s*=\s*["\']?(\w+)')
RE_API_ID = re.compile(r'["\'`](claude-(?:fable|mythos|opus|sonnet|haiku)-[0-9][\w.\-]*)["\'`]')
RE_SO_TEXTO = re.compile(r'^(?:(?:echo|printf|log|logger|say|warn|info)\b|print\(|console\.(?:log|error)\()')
RE_API_EF = re.compile(r'effort["\']?\s*[:=]\s*["\'](low|medium|high|xhigh|max)["\']')


def familia(m):
    """'claude-fable-5-2' / 'fable' / 'opus[1m]' / '$MODELO' -> fable|mythos|opus|sonnet|haiku|variavel|outro."""
    if not m:
        return None
    s = str(m).lower()
    if s.startswith('$') or '${' in s or s.startswith('%') or s.startswith('{{'):
        return 'variavel'
    for f in ('mythos', 'fable', 'opus', 'sonnet', 'haiku'):
        if f in s:
            return f
    if s.startswith('gpt') or s.startswith('o3') or s.startswith('o4'):
        return 'codex'
    return 'outro'


def esforco_ok(e):
    if not e:
        return None
    s = str(e).lower().strip('"\'')
    if s.startswith('$') or '${' in s:
        return 'variavel'
    return s if s in ESFORCOS else s


class Auditoria:
    def __init__(self, anonimo=False, docs=False):
        self.achados = []
        self.anonimo = anonimo
        self.docs = docs
        self.home = str(Path.home())
        self.vistos = set()

    def caminho(self, p):
        s = str(p)
        try:  # dentro da pasta atual: caminho relativo, mais curto e sem a pasta pessoal
            rel = Path(s).resolve().relative_to(Path.cwd().resolve())
            return './' + str(rel) if str(rel) != '.' else '.'
        except (ValueError, OSError):
            pass
        if self.anonimo and s.startswith(self.home):
            s = '~' + s[len(self.home):]
        return s

    def add(self, p, linha, tipo, ferramenta, modelo, esforco, trecho, padrao_global=False, chave=''):
        visto = (str(p), linha, tipo, modelo, esforco)
        if visto in self.vistos:
            return
        self.vistos.add(visto)
        self.achados.append({
            'onde': f'{self.caminho(p)}:{linha}', 'tipo': tipo, 'ferramenta': ferramenta,
            'modelo': modelo, 'familia': familia(modelo), 'esforco': esforco_ok(esforco),
            'padrao_global': padrao_global, 'chave': chave, 'trecho': trecho.strip()[:140],
        })

    # ---------- leitores ----------
    def settings(self, p, global_=False):
        try:
            txt = p.read_text(encoding='utf-8', errors='replace')
            dado = json.loads(txt)
        except Exception:
            return
        linhas = txt.splitlines()
        usadas = set()

        def linha_de(chave, valor):
            # a mesma chave/valor pode aparecer várias vezes (ex.: effortLevel por modelo): cada achado pega a próxima linha livre
            for i, l in enumerate(linhas, 1):
                if f'"{chave}"' in l and str(valor) in l and i not in usadas:
                    usadas.add(i)
                    return i
            return 1

        def anda(o, caminho=''):
            if isinstance(o, dict):
                for k, v in o.items():
                    sub = f'{caminho}.{k}' if caminho else k
                    if k == 'model' and isinstance(v, str):
                        self.add(p, linha_de(k, v), 'settings', 'claude', v, None, f'{sub} = {v}', padrao_global=(sub == 'model'), chave=sub)
                    elif k == 'effortLevel' and isinstance(v, str):
                        # modelSettings.<modelo>.effortLevel = esforço padrão daquele modelo (vale para toda sessão com ele)
                        pm = re.match(r'modelSettings\.(.+)\.effortLevel$', sub)
                        self.add(p, linha_de(k, v), 'settings', 'claude', pm.group(1) if pm else None, v, f'{sub} = {v}',
                                 padrao_global=(sub == 'effortLevel' or bool(pm)), chave=sub)
                    elif k == 'ANTHROPIC_MODEL' and isinstance(v, str):
                        self.add(p, linha_de(k, v), 'settings', 'claude', v, None, f'{sub} = {v}', padrao_global=True, chave=sub)
                    else:
                        anda(v, sub)
            elif isinstance(o, list):
                for x in o:
                    anda(x, caminho)
        anda(dado)

    def frontmatter(self, p, tipo):
        try:
            txt = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            return
        if not txt.startswith('---'):
            return
        fim = txt.find('\n---', 3)
        if fim < 0:
            return
        bloco = txt[3:fim].splitlines()
        modelo = esforco = None
        lm = le = 1
        for i, l in enumerate(bloco, 2):
            m = re.match(r'\s*model\s*:\s*["\']?([^"\'#\s]+)', l)
            e = re.match(r'\s*effort\s*:\s*["\']?([^"\'#\s]+)', l)
            if m:
                modelo, lm = m.group(1), i
            if e:
                esforco, le = e.group(1), i
        if modelo or esforco:
            nome = p.parent.name if p.name == 'SKILL.md' else p.stem
            self.add(p, lm if modelo else le, tipo, 'claude', modelo, esforco, f'{tipo} {nome}: model={modelo or "herda"} effort={esforco or "herda"}')

    def script(self, p):
        try:
            if p.stat().st_size > MAX_BYTES:
                return
            txt = p.read_text(encoding='utf-8', errors='strict')
        except Exception:
            return
        # junta linhas quebradas com "\" para ler o comando inteiro
        brutas = txt.splitlines()
        i = 0
        while i < len(brutas):
            ini = i + 1
            linha = brutas[i]
            while linha.rstrip().endswith('\\') and i + 1 < len(brutas):
                i += 1
                linha = linha.rstrip()[:-1] + ' ' + brutas[i].strip()
            i += 1
            s = linha.strip()
            if not s or s.startswith('#') and not s.startswith('#!'):
                continue
            if RE_SO_TEXTO.match(s):  # echo/log/print de uma frase que cita o comando não roda nada
                continue
            if RE_CLAUDE.search(s) and ('-p' in s.split() or '--print' in s or '--model' in s or '--effort' in s):
                m = RE_MODEL_FLAG.search(s)
                e = RE_EFFORT_FLAG.search(s)
                self.add(p, ini, 'script', 'claude', m.group(2) if m else None, e.group(2) if e else None, s)
            elif RE_CODEX.search(s):
                m = RE_CODEX_M.search(s)
                e = RE_CODEX_EF.search(s)
                self.add(p, ini, 'script', 'codex', m.group(2) if m else None, e.group(1) if e else None, s)
            for m in RE_API_ID.finditer(s):
                e = RE_API_EF.search(s)
                self.add(p, ini, 'api', 'api', m.group(1), e.group(1) if e else None, s)

    def pasta(self, raiz):
        raiz = Path(raiz).expanduser().resolve()
        if raiz.is_file():
            self.arquivo(raiz)
            return
        for dirpath, dirnames, filenames in os.walk(raiz):
            dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIR and not d.endswith('.egg-info')]
            for f in filenames:
                self.arquivo(Path(dirpath) / f)

    def arquivo(self, p):
        nome, ext = p.name, p.suffix.lower()
        if self.eu_mesmo(p):  # o auditor copiado para o projeto (ex.: tools/auditar.py) não audita a si mesmo
            return
        partes = p.parts
        if p.is_symlink() and not p.exists():
            return
        if '.claude' in partes and nome.startswith('settings') and ext == '.json':
            self.settings(p)
        elif 'agents' in partes and ext == '.md':
            self.frontmatter(p, 'agente')
        elif nome == 'SKILL.md':
            self.frontmatter(p, 'skill')
        elif 'commands' in partes and '.claude' in partes and ext == '.md':
            self.frontmatter(p, 'comando')
        elif ext in EXT_SCRIPT or nome in NOMES_SCRIPT or (self.docs and ext in EXT_DOCS):
            self.script(p)
        elif not ext and p.is_file():
            try:
                with open(p, 'rb') as fh:
                    if fh.read(2) == b'#!':
                        self.script(p)
            except Exception:
                pass

    def eu_mesmo(self, p):
        try:
            if p.resolve() == Path(__file__).resolve():
                return True
            if p.suffix == '.py' and p.stat().st_size < 200_000:
                with open(p, encoding='utf-8', errors='replace') as fh:
                    return MARCA in fh.read(400)
        except OSError:
            pass
        return False

    def home_claude(self):
        h = Path.home()
        for p in [h / '.claude' / 'settings.json', h / '.claude' / 'settings.local.json']:
            if p.exists():
                self.settings(p, global_=True)
        for d, tipo in [(h / '.claude' / 'agents', 'agente'), (h / '.claude' / 'commands', 'comando')]:
            if d.is_dir():
                for p in sorted(d.glob('*.md')):
                    self.frontmatter(p, tipo)
        sk = h / '.claude' / 'skills'
        if sk.is_dir():
            for p in sorted(sk.glob('*/SKILL.md')):
                self.frontmatter(p, 'skill')
        un = h / '.config' / 'systemd' / 'user'
        if un.is_dir():
            for p in sorted(un.glob('*.service')):
                self.script(p)

    # ---------- alertas ----------
    def alertas(self):
        out = []
        for a in self.achados:
            ef, fam = a['esforco'], a['familia']
            if ef == 'max':
                out.append(('MAX', a, 'Esforço Max fixo. No FrontierCode 2.0 o Max fez menos que o Xhigh e custou ~3x mais. '
                                      'Troque por high (ou xhigh se o resultado pedir) e meça com o ab.sh.'))
            elif ef == 'xhigh' and a['padrao_global']:
                quem = f'do {a["modelo"]}' if a['modelo'] else 'global'
                out.append(('PADRAO_ALTO', a, f'Xhigh como padrão {quem}: todo pedido paga o topo. Deixe medium/high '
                                              'como padrão e suba o esforço só na tarefa difícil.'))
            if fam in ('fable', 'mythos') and a['padrao_global'] and a['chave'] in ('model', 'env.ANTHROPIC_MODEL'):
                out.append(('FABLE_PADRAO', a, 'Fable como modelo padrão gasta o limite mais rápido. A Anthropic recomenda '
                                               'o Opus 5.5 no dia a dia e o Fable no trabalho mais difícil.'))
        return out

    def dicas(self):
        out = []
        for a in self.achados:
            if a['tipo'] == 'script' and a['ferramenta'] == 'claude' and not a['modelo']:
                out.append((a, 'claude sem --model: herda o padrão da conta (pode mudar sem você ver). Fixe o modelo.'))
            elif a['tipo'] == 'script' and a['familia'] in ('fable', 'mythos') and not a['esforco']:
                out.append((a, 'Fable sem --effort: no Claude Code o padrão é medium. Diga o esforço que você quer.'))
            elif a['tipo'] == 'api' and a['familia'] in ('fable', 'mythos') and not a['esforco']:
                out.append((a, 'Chamada de API com Fable sem esforço na mesma linha: confira qual esforço ela usa e deixe explícito.'))
        return out


def contagem(achados, campo):
    c = {}
    for a in achados:
        k = a[campo] or ('herda' if campo == 'familia' else 'padrão')
        c[k] = c.get(k, 0) + 1
    return c


def relatorio_md(aud, pastas):
    al, di = aud.alertas(), aud.dicas()
    L = [f'# Auditoria de modelo e esforço — {date.today().isoformat()}', '',
         f'Pastas: {", ".join(pastas)} · esforco-certo {VERSAO}', '',
         f'**{len(aud.achados)} lugares** fixam modelo ou esforço · **{len(al)} alertas** · {len(di)} dicas', '']
    fam = contagem(aud.achados, 'familia')
    ef = contagem(aud.achados, 'esforco')
    L.append('Modelos: ' + ' · '.join(f'{k} {v}' for k, v in sorted(fam.items(), key=lambda x: -x[1])))
    L.append('Esforços: ' + ' · '.join(f'{k} {v}' for k, v in sorted(ef.items(), key=lambda x: -x[1])))
    L.append('')
    if al:
        L += ['## Alertas (custam caro sem precisar)', '']
        for cod, a, msg in al:
            L.append(f'- **{cod}** `{a["onde"]}` — {msg}')
        L.append('')
    if di:
        L += ['## Dicas', '']
        for a, msg in di[:40]:
            L.append(f'- `{a["onde"]}` — {msg}')
        if len(di) > 40:
            L.append(f'- … e mais {len(di) - 40}')
        L.append('')
    L += ['## Tudo o que foi achado', '', '| Onde | Tipo | Ferramenta | Modelo | Esforço |', '|---|---|---|---|---|']
    for a in sorted(aud.achados, key=lambda x: x['onde']):
        L.append(f'| `{a["onde"]}` | {a["tipo"]}{" (padrão)" if a["padrao_global"] else ""} | {a["ferramenta"]} | '
                 f'{a["modelo"] or "herda"} | {a["esforco"] or "padrão"} |')
    L += ['', '## A regra (cole no CLAUDE.md: politica/CLAUDE-esforco.md)', '',
          '1. Padrão do dia a dia: **Opus 5.5, esforço medium** (é o que o Claude Code já usa).',
          '2. Trabalho longo e difícil (migração, auditoria, agentes por horas): **Fable, esforço high**.',
          '3. **Xhigh** só quando a nota importa e você mediu; **Max** só com teste que prove ganho.',
          '4. Tarefa mecânica (renomear, extrair, formatar): **Haiku ou Sonnet, esforço low**.', '']
    return '\n'.join(L)


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    flags = {a for a in argv if a.startswith('--')}
    if '--help' in flags or '-h' in argv:
        print(__doc__)
        return 0
    if '--versao' in flags:
        print(VERSAO)
        return 0
    pastas = args or ['.']
    aud = Auditoria(anonimo='--anonimo' in flags, docs='--docs' in flags)
    for p in pastas:
        if not Path(p).expanduser().exists():
            print(f'pasta não existe: {p}', file=sys.stderr)
            return 2
        aud.pasta(p)
    if '--home' in flags:
        aud.home_claude()
        pastas = pastas + ['~/.claude']
    nomes = [aud.caminho(Path(p).expanduser().resolve()) if p != '~/.claude' else p for p in pastas]
    al = aud.alertas()
    if '--json' in flags:
        print(json.dumps({'versao': VERSAO, 'data': date.today().isoformat(), 'pastas': nomes, 'achados': aud.achados,
                          'alertas': [{'codigo': c, 'onde': a['onde'], 'msg': m} for c, a, m in al],
                          'dicas': [{'onde': a['onde'], 'msg': m} for a, m in aud.dicas()]}, ensure_ascii=False, indent=1))
    else:
        print(relatorio_md(aud, nomes))
    return 1 if ('--estrito' in flags and al) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
