# Minimal Recursive Self-Improvement Loop with a Code Agent

## Research question
Can a code agent improve its own scaffold (the program that solves tasks)
over successive iterations, as measured by a fixed benchmark?

## Hypothesis
The pass rate on held-out tasks increases from iteration 0 to iteration 5.

## Setup
- Benchmark: 20 small Python tasks, each with unit tests
  (12 for optimization, 8 held out for final evaluation).
- Scaffold: `scaffold.py`, the only file the agent may modify.
- Agent: Codex (model "6.1 Sol", effort "High").
- Iterations: 5 (iteration 0 is the baseline).

## Metric
Pass rate = tests passed / total tests, on the optimization set and on the held-out set.

## Protocol
1. Run the evaluation on the current `scaffold.py` and save the score in `results/`.
2. Give the agent the failing tests and ask it to improve `scaffold.py`.
3. Save the new version as `versions/scaffold_iter_N.py`.
4. Repeat 5 times.

## Rules
- The agent may only modify `scaffold.py`.
- The held-out tasks are never shown to the agent.
- Every score is saved, including failed iterations.

## Limitations (to be completed)
Small benchmark, one run, one model.
