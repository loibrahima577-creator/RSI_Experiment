"""Generate and evaluate solutions against the task benchmark."""

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import scaffold


ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"

_TEST_RUNNER = r'''
import ast
import json
from pathlib import Path

passed = 0
failed = 0

def report(ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
    print("@@RESULT@@" + json.dumps({"passed": passed, "failed": failed}), flush=True)

def execute_test(node, namespace):
    try:
        module = ast.Module(body=[node], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "tests.py", "exec"), namespace)
    except Exception:
        report(False)
    else:
        report(True)

def execute_loop(node, namespace):
    values = eval(compile(ast.Expression(node.iter), "tests.py", "eval"), namespace)
    for value in values:
        assign = ast.Assign(targets=[node.target], value=ast.Constant(value=value))
        module = ast.Module(body=[ast.fix_missing_locations(assign)], type_ignores=[])
        exec(compile(module, "tests.py", "exec"), namespace)
        for child in node.body:
            execute_unit(child, namespace)

def execute_unit(node, namespace):
    if isinstance(node, ast.For):
        execute_loop(node, namespace)
    else:
        execute_test(node, namespace)

namespace = {"__name__": "__main__", "__file__": "tests.py"}
tree = ast.parse(Path("tests.py").read_text(encoding="utf-8"), filename="tests.py")
for node in tree.body:
    if isinstance(node, ast.Assert):
        execute_test(node, namespace)
    elif isinstance(node, (ast.Try, ast.For)):
        execute_unit(node, namespace)
    else:
        exec(compile(ast.Module(body=[node], type_ignores=[]), "tests.py", "exec"), namespace)
print("@@SUMMARY@@" + json.dumps({"passed": passed, "failed": failed}), flush=True)
'''


def _test_count(statements) -> int:
    count = 0
    for statement in statements:
        if isinstance(statement, (ast.Assert, ast.Try)):
            count += 1
        elif isinstance(statement, ast.For):
            values = ast.literal_eval(statement.iter)
            count += len(values) * _test_count(statement.body)
    return count


def _parse_progress(output: str) -> tuple[int, int]:
    passed = failed = 0
    for line in output.splitlines():
        if line.startswith("@@RESULT@@") or line.startswith("@@SUMMARY@@"):
            try:
                result = json.loads(line.split("@@", 2)[-1])
                passed, failed = result["passed"], result["failed"]
            except (ValueError, KeyError):
                continue
    return passed, failed


def _evaluate_task(task_id: str, prompt: str, tests_source: str, tests_total: int) -> dict:
    try:
        solution = scaffold.solve(prompt)
    except Exception:
        return {
            "task_id": task_id,
            "status": "generation_error",
            "tests_passed": 0,
            "tests_total": tests_total,
            "error": "solution generation failed",
        }

    with TemporaryDirectory(prefix=f"{task_id}_") as temporary:
        task_dir = Path(temporary)
        (task_dir / "solution.py").write_text(solution, encoding="utf-8")
        (task_dir / "tests.py").write_text(tests_source, encoding="utf-8")
        try:
            completed = subprocess.run(
                [sys.executable, "-c", _TEST_RUNNER],
                cwd=task_dir,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            passed, failed = _parse_progress(completed.stdout)
            status = "passed" if completed.returncode == 0 and failed == 0 else "failed"
            if completed.returncode != 0 and passed + failed < tests_total:
                failed += tests_total - passed - failed
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            passed, failed = _parse_progress(stdout)
            failed += max(1, tests_total - passed - failed)
            status = "timeout"

    return {
        "task_id": task_id,
        "status": status,
        "tests_passed": min(passed, tests_total),
        "tests_total": tests_total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", dest="task_set", choices=("optimization", "heldout"), required=True)
    parser.add_argument("--iter", dest="iteration", type=int, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be nonnegative")

    split = json.loads((TASKS_DIR / "split.json").read_text(encoding="utf-8"))
    task_ids = split[f"{args.task_set}_set"]
    if args.limit is not None:
        task_ids = task_ids[:args.limit]

    task_results = []
    for task_id in task_ids:
        task_dir = TASKS_DIR / task_id
        prompt = (task_dir / "prompt.md").read_text(encoding="utf-8")
        tests_source = (task_dir / "tests.py").read_text(encoding="utf-8")
        test_tree = ast.parse(tests_source, filename="tests.py")
        tests_total = _test_count(test_tree.body)
        task_results.append(_evaluate_task(task_id, prompt, tests_source, tests_total))

    tests_passed = sum(result["tests_passed"] for result in task_results)
    tests_total = sum(result["tests_total"] for result in task_results)
    result_data = {
        "iteration": args.iteration,
        "set": args.task_set,
        "tasks_evaluated": len(task_results),
        "tests_passed": tests_passed,
        "tests_total": tests_total,
        "pass_rate": tests_passed / tests_total if tests_total else 0.0,
        "task_results": task_results,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    output_path = RESULTS_DIR / f"iter_{args.iteration}_{args.task_set}.json"
    output_path.write_text(json.dumps(result_data, indent=2) + "\n", encoding="utf-8")
    print(f"Saved results to {output_path.relative_to(ROOT)}")
    print(f"Pass rate: {tests_passed}/{tests_total} ({result_data['pass_rate']:.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
