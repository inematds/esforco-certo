# Comparar dois modelos sem se enganar: capacidade, interpretação ou esforço?

Uma comparação de "mesmo prompt, qual ficou mais bonito" mistura três coisas:

| Fator | A pergunta | Como aparece |
|---|---|---|
| **Capacidade** | O modelo enxerga sozinho como melhorar o projeto, sem receber a instrução? | Detalhes que ninguém pediu e que fazem sentido |
| **Interpretação** | Ele entendeu melhor o objetivo e decidiu certo? | Cumpre o que foi pedido — inclusive o que estava implícito |
| **Esforço** | Ele gastou mais tempo, raciocínio, ferramentas e dinheiro? | Rodou mais, chamou mais ferramentas, custou mais |

Se um modelo roda bem mais tempo e gasta bem mais, parte da diferença pode ser só **mais esforço**, não mais inteligência.
E "foi além do pedido" (animação, imagem, personagem) impressiona quem avalia, mas não é o mesmo que **resolver melhor o
pedido**: num jogo, ficar mais bonito e perder na jogabilidade é resolver pior.

## Os três experimentos

Rode os três antes de concluir qual modelo é "melhor" para você. Cada um responde uma pergunta diferente.

### 1. Mesmo pedido, mesmo orçamento

Mesmo prompt, mesmo teto de turnos e de tempo, mesmas ferramentas.
**Responde:** quem entrega mais qualidade com recursos iguais.

```bash
./ab.sh "<tarefa>" --dir <projeto> --turnos 30 -c opus:high -c fable:high
```

O `--turnos` vale igual para todas as combinações; o quadro mostra tempo, tokens e custo equivalente de cada uma.

### 2. Mesmo pedido, melhor esforço

Mesmo prompt inicial, cada modelo no esforço em que ele rende mais, sem teto apertado. Registre todo o custo.
**Responde:** qual produz o melhor resultado final — e quanto custa chegar lá.

```bash
./ab.sh "<tarefa>" --dir <projeto> -c opus:xhigh -c fable:xhigh
```

### 3. Mesmo resultado esperado

Os dois recebem os mesmos critérios objetivos (funciona? passa nos testes? cumpre cada requisito?) e trabalham até
atingir o padrão. Meça **quantas rodadas, correções e minutos seus** foram necessários.
**Responde:** quanto custa, no total, transformar a especificação em produto pronto.

```bash
./ab.sh "<tarefa com os critérios escritos>" --dir <projeto> --editar --checar "npm ci && npm test" -c opus:high -c fable:high
```

O `ab.sh` roda uma rodada por combinação. Se o teste não passou, peça a correção e rode de novo; anote cada rodada na
ficha abaixo.

## Ficha de avaliação (copie para o seu projeto)

Antes de ver o resultado, escreva os critérios. Depois, dê nota separando **o que foi pedido** de **o que veio a mais**.

| Critério | Peso | Modelo A | Modelo B |
|---|---|---|---|
| Cumpre cada requisito pedido (lista) | 40% | | |
| Funciona / passa nos testes | 30% | | |
| Acabamento do que foi pedido | 15% | | |
| Extras úteis (não pedidos) | 5% | | |
| Erros ou regressões | −10% cada | | |
| **Tempo** (min) · **custo** · **rodadas** · **seus minutos de correção** | — | | |

Regras da ficha:

- **Extra não pedido vale pouco** se o pedido não foi cumprido. Bonito que não funciona não ganha.
- **Mesmo avaliador, sem saber qual é qual** (renomeie as pastas para A e B antes de olhar).
- **Custo total = modelo + seu tempo.** Uma hora sua corrigindo pesa mais que alguns dólares de token.

## O que uma tentativa única NÃO prova

Uma rodada de "mesmo prompt, qual ficou mais bonito" não mostra que um modelo:

- interpreta melhor todos os requisitos;
- escreve código melhor;
- comete menos erros;
- precisa de menos intervenções;
- entrega mais produtividade por dólar;
- ganhou por capacidade, e não por ter trabalhado mais.

A pergunta certa não é qual modelo faz a tela mais bonita numa tentativa. É **qual transforma uma especificação em
produto excelente e funcional com o menor custo total**.
