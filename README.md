# A Minimal Recursive Self-Improvement Loop with Code Agents

A small, fully reproducible experiment: can a code-generating scaffold improve itself from failure feedback, and does the gain transfer to held-out tasks?

**Read the article: [ARTICLE.md](ARTICLE.md)**
Companion literature review: [RSI_Review](https://github.com/loibrahima577-creator/RSI_Review)

## Main result

| Condition | Optimization (12 tasks) | Held-out (8 tasks) |
|---|---|---|
| Baseline scaffold | 30.7 % ± 1.1 | 52.8 % ± 2.1 |
| Final scaffold (iteration 5) | 76.3 % ± 4.0 | 86.1 % ± 1.1 |

Mean ± std over 4 evaluations of the same scaffold. Pass rate = test assertions passed / total.
This is a single improvement trajectory on a small benchmark: see the limitations below.

## Setup

- Benchmark: 20 small Python tasks (`tasks_v2/`) with hidden house conventions checked by tests; split into 12 optimization and 8 held-out tasks (`tasks_v2/split.json`).
- Solver: `gpt-5.6-luna`, low effort, running `scaffold.py` (one LLM call per task).
- Improver: `gpt-6.1-sol`, high effort. It rewrites `scaffold.py` using only failures from the optimization set.
- Iterations: 5. Every candidate scaffold passes an AST safety check before use.
- `tasks/` (v1) was saturated (about 100 % at baseline) and is kept as evidence of a ceiling effect.

## Reproduce

Requires Python, `matplotlib`, and API access (the key is read at run time from `~/.codex/auth.json` and is never stored in this repository).

```powershell
python list_models.py
python evaluate.py --set optimization --iter 0 --tasks tasks_v2 --model gpt-5.6-luna
python run_loop.py --tasks tasks_v2 --model gpt-5.6-luna --iterations 5
python audit_leakage.py
python analyze_results.py
```

LLM outputs are non-deterministic: exact numbers will vary between runs.

## Repository layout

- `versions/`: every scaffold version (`scaffold_iter_0.py` … `scaffold_iter_5.py`)
- `logs/`: improver prompts and responses
- `results/`: JSON and CSV results, `leakage_audit.txt`
- `figures/`: figures used in the article
- `private/conventions.md`: the hidden conventions used in the v2 tests

## Limitations

- One improvement trajectory: the error bars measure evaluation noise, not the variability of the improvement loop.
- Held-out tasks share the optimization tasks' hidden conventions, so generalization is across tasks with the same conventions, not to unseen rules.
- The benchmark was designed to leave headroom after v1 saturated.
- Small scale (20 tasks), one solver model, one improver model.
- Candidates are accepted if they pass the safety check; there is no rollback on performance.

See the article for details.