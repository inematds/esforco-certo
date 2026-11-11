# Comparing Two Models Without Fooling Yourself: Capability, Interpretation, or Effort?

A comparison of “same prompt, which one looked better” mixes three things:

| Factor | The question | How it shows up |
|---|---|---|
| **Capability** | Can the model see on its own how to improve the project without being given the instruction? | Details nobody asked for that make sense |
| **Interpretation** | Did it understand the goal better and make the right decisions? | Fulfills what was requested—including what was implied |
| **Effort** | Did it spend more time, reasoning, tools, and money? | Ran longer, called more tools, cost more |

If one model runs for much longer and spends much more, part of the difference may be **more effort** alone, not more intelligence.
And “went beyond the request” (animation, image, character) impresses whoever evaluates it, but it is not the same as **fulfilling the request better**: in a game, looking better but losing on gameplay means doing a worse job.

## The Three Experiments

Run all three before deciding which model is “better” for you. Each answers a different question.

### 1. Same Request, Same Budget

Same prompt, same cap on turns and time, same tools.  
**Answers:** who delivers higher quality with equal resources.

```bash
./ab.sh "<task>" --dir <project> --turnos 30 -c opus:high -c fable:high
```

`--turnos` applies equally to all combinations; the table shows each one's time, tokens, and equivalent cost.

### 2. Same Request, Best Effort

Same initial prompt, each model at the effort level where it performs best, with no tight cap. Record the full cost.  
**Answers:** which produces the best final result—and how much it costs to get there.

```bash
./ab.sh "<task>" --dir <project> -c opus:xhigh -c fable:xhigh
```

### 3. Same Expected Result

Both receive the same objective criteria (does it work? pass the tests? meet every requirement?) and work until they reach the standard. Measure **how many rounds, corrections, and minutes of your time** were needed.  
**Answers:** the total cost of turning the specification into a finished product.

```bash
./ab.sh "<task with the criteria written out>" --dir <project> --editar --checar "npm ci && npm test" -c opus:high -c fable:high
```

`ab.sh` runs one round per combination. If the test does not pass, ask for a correction and run it again; record each round on the scorecard below.

## Evaluation Scorecard (Copy to Your Project)

Write down the criteria before seeing the results. Then score them, separating **what was requested** from **what was added**.

| Criterion | Weight | Model A | Model B |
|---|---|---|---|
| Meets every requested requirement (list) | 40% | | |
| Works / passes the tests | 30% | | |
| Polish of what was requested | 15% | | |
| Useful extras (not requested) | 5% | | |
| Errors or regressions | −10% each | | |
| **Time** (min) · **cost** · **rounds** · **your correction minutes** | — | | |

Scorecard rules:

- **Unrequested extras count for little** if the request was not fulfilled. Something beautiful that does not work does not win.
- **Use the same evaluator, without knowing which is which** (rename the folders A and B before looking).
- **Total cost = model + your time.** An hour of your time spent correcting weighs more than a few dollars in tokens.

## What a Single Attempt Does NOT Prove

One round of “same prompt, which one looked better” does not show that a model:

- interprets every requirement better;
- writes better code;
- makes fewer mistakes;
- needs fewer interventions;
- delivers more productivity per dollar;
- won because of capability rather than having worked more.

The right question is not which model makes the prettiest screen in one attempt. It is **which one turns a specification into an excellent, functional product at the lowest total cost**.
