"""Testes do auditar.py (sem rede): python3 -m unittest discover tests"""
import json, subprocess, sys, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FIX = RAIZ / 'tests' / 'fixture'
sys.path.insert(0, str(RAIZ))
import auditar  # noqa: E402


def rodar(*args):
    r = subprocess.run([sys.executable, str(RAIZ / 'auditar.py'), *args], capture_output=True, text=True)
    return r.returncode, r.stdout


class TestAuditar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rc, out = rodar(str(FIX), '--json')
        cls.d = json.loads(out)
        cls.ach = cls.d['achados']

    def acha(self, **kw):
        return [a for a in self.ach if all(a.get(k) == v for k, v in kw.items())]

    def test_settings_padrao_global(self):
        self.assertTrue(self.acha(tipo='settings', familia='fable', padrao_global=True))
        self.assertTrue(self.acha(tipo='settings', esforco='xhigh', padrao_global=True))
        self.assertTrue(self.acha(tipo='settings', modelo='claude-opus-5-5'))

    def test_agentes_frontmatter(self):
        self.assertTrue(self.acha(tipo='agente', familia='fable', esforco='max'))
        self.assertTrue(self.acha(tipo='agente', familia='haiku', esforco='low'))

    def test_script_linhas_quebradas(self):
        self.assertTrue(self.acha(tipo='script', familia='fable', esforco='max'))
        self.assertTrue(self.acha(tipo='script', familia='opus', esforco='high'))

    def test_script_sem_modelo_e_variavel(self):
        self.assertTrue(self.acha(tipo='script', ferramenta='claude', modelo=None))
        self.assertTrue(self.acha(tipo='script', familia='variavel', esforco='variavel'))

    def test_codex(self):
        self.assertTrue(self.acha(ferramenta='codex', modelo='gpt-6-astra', esforco='high'))

    def test_api(self):
        self.assertTrue(self.acha(tipo='api', modelo='claude-fable-5-2', esforco=None))
        self.assertTrue(self.acha(tipo='api', modelo='claude-opus-5-5', esforco='max'))

    def test_comentario_e_docs_ficam_fora(self):
        self.assertFalse([a for a in self.ach if 'README' in a['onde']])
        self.assertFalse([a for a in self.ach if 'não conta' in a['trecho']])
        _, out = rodar(str(FIX), '--json', '--docs')
        self.assertTrue([a for a in json.loads(out)['achados'] if 'README' in a['onde']])

    def test_alertas(self):
        cods = {a['codigo'] for a in self.d['alertas']}
        self.assertEqual(cods, {'MAX', 'PADRAO_ALTO', 'FABLE_PADRAO'})
        self.assertEqual(self.rc, 0)

    def test_estrito_falha_com_alerta(self):
        rc, _ = rodar(str(FIX), '--estrito')
        self.assertEqual(rc, 1)
        rc, _ = rodar(str(FIX / 'scripts' / 'rodar.sh'), '--estrito')  # arquivo avulso também roda
        self.assertEqual(rc, 1)

    def test_markdown(self):
        _, out = rodar(str(FIX))
        self.assertIn('## Alertas', out)
        self.assertIn('| Onde | Tipo |', out)

    def test_esforco_por_modelo_e_linhas_distintas(self):
        por_modelo = self.acha(tipo='settings', esforco='xhigh', padrao_global=True)
        self.assertEqual({a['modelo'] for a in por_modelo}, {None, 'claude-opus-5-5', 'claude-fable-5-1'})
        self.assertEqual(len({a['onde'] for a in por_modelo}), 3)

    def test_fable_padrao_so_pela_chave_model(self):
        fab = [a for a in self.d['alertas'] if a['codigo'] == 'FABLE_PADRAO']
        self.assertEqual(len(fab), 1)  # modelSettings.claude-fable-5-1.effortLevel não é "Fable como padrão"

    def test_log_e_echo_nao_contam(self):
        self.assertFalse([a for a in self.ach if a['trecho'].startswith(('log ', 'echo '))])

    def test_familia(self):
        self.assertEqual(auditar.familia('opus[1m]'), 'opus')
        self.assertEqual(auditar.familia('${M}'), 'variavel')
        self.assertEqual(auditar.familia('claude-mythos-5-2'), 'mythos')
        self.assertIsNone(auditar.familia(None))

    def test_ab_argumentos(self):
        ab = str(RAIZ / 'ab.sh')
        self.assertEqual(subprocess.run(['bash', '-n', ab]).returncode, 0)
        self.assertEqual(subprocess.run(['bash', ab], capture_output=True).returncode, 2)            # sem tarefa
        r = subprocess.run(['bash', ab, 'x', '-c', 'opus:turbo'], capture_output=True, text=True)    # esforço inválido
        self.assertEqual(r.returncode, 2)
        self.assertIn('esforço inválido', r.stderr)

    def test_pasta_inexistente(self):
        rc, _ = rodar('/nao/existe/mesmo')
        self.assertEqual(rc, 2)


if __name__ == '__main__':
    unittest.main()
