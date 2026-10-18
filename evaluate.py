"""Generate and evaluate solutions against the task benchmark."""

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"

_TEST_RUNNER = r'''
import ast
import json
from pathlib import Path

passed = 0
failed = 0
failure_messages = []

def report(ok, message=None):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        failure_messages.append(message or "assertion failed")
    print("@@RESULT@@" + json.dumps({
        "passed": passed,
        "failed": failed,
        "failure_messages": failure_messages,
    }), flush=True)

def execute_test(node, namespace):
    try:
        module = ast.Module(body=[node], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "tests.py", "exec"), namespace)
    except Exception as exc:
        expression = ast.unparse(node)
        message = str(exc) or expression
        report(False, f"{type(exc).__name__}: {message}")
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
print("@@SUMMARY@@" + json.dumps({
    "passed": passed,
    "failed": failed,
    "failure_messages": failure_messages,
}), flush=True)
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


def _parse_progress(output: str) -> tuple[int, int, list[str]]:
    passed = failed = 0
    failure_messages = []
    for line in output.splitlines():
        if line.startswith("@@RESULT@@") or line.startswith("@@SUMMARY@@"):
            try:
                result = json.loads(line.split("@@", 2)[-1])
                passed, failed = result["passed"], result["failed"]
                failure_messages = result.get("failure_messages", [])
            except (ValueError, KeyError):
                continue
    return passed, failed, failure_messages


def _load_solver(scaffold_path: str | Path):
    path = Path(scaffold_path)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    spec = importlib.util.spec_from_file_location("_experiment_scaffold", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load scaffold: {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    solve = getattr(module, "solve", None)
    if not callable(solve):
        raise TypeError("Scaffold must define callable solve")
    return solve


def _evaluate_task(
    task_id: str,
    prompt: str,
    tests_source: str,
    tests_total: int,
    solve,
    model: str | None = None,
) -> dict:
    generation_error = None
    for _attempt in range(2):
        try:
            solution = solve(prompt, model=model)
            break
        except Exception as exc:
            generation_error = exc
    else:
        return {
            "task_id": task_id,
            "status": "generation_error",
            "tests_passed": 0,
            "tests_total": tests_total,
            "error_type": type(generation_error).__name__,
            "error_message": str(generation_error),
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
            passed, failed, failure_messages = _parse_progress(completed.stdout)
            status = "passed" if completed.returncode == 0 and failed == 0 else "failed"
            if completed.returncode != 0 and passed + failed < tests_total:
                failed += tests_total - passed - failed
            if completed.returncode != 0 and not failure_messages:
                failure_messages.append(completed.stderr.strip() or "test subprocess failed")
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            passed, failed, failure_messages = _parse_progress(stdout)
            failed += max(1, tests_total - passed - failed)
            failure_messages.append("test subprocess timed out")
            status = "timeout"

    return {
        "task_id": task_id,
        "status": status,
        "tests_passed": min(passed, tests_total),
        "tests_total": tests_total,
        "generated_solution": solution,
        "failing_assertions": failure_messages,
    }


def _result_path(iteration: int, tasks: str | Path, task_set: str, model: str | None) -> Path:
    tasks_name = Path(tasks).name
    safe_tasks = re.sub(r"[^A-Za-z0-9_.-]+", "_", tasks_name).strip("._") or "tasks"
    suffix = ""
    if model:
        safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model).strip("._") or "model"
        suffix = f"_{safe_model}"
    return RESULTS_DIR / f"iter_{iteration}_{safe_tasks}_{task_set}{suffix}.json"


def evaluate_set(
    tasks: str | Path = "tasks",
    task_set: str = "optimization",
    iteration: int = 0,
    model: str | None = None,
    scaffold_path: str | Path = "scaffold.py",
    limit: int | None = None,
) -> dict:
    tasks_path = Path(tasks)
    if not tasks_path.is_absolute():
        tasks_path = ROOT / tasks_path
    scaffold_file = Path(scaffold_path)
    if not scaffold_file.is_absolute():
        scaffold_file = ROOT / scaffold_file
    scaffold_file = scaffold_file.resolve()
    split = json.loads((tasks_path / "split.json").read_text(encoding="utf-8"))
    task_ids = split["optimization_set" if task_set == "optimization" else "held_out_set"]
    if limit is not None:
        task_ids = task_ids[:limit]
    solve = _load_solver(scaffold_file)
    task_results = []
    for task_id in task_ids:
        task_dir = tasks_path / task_id
        prompt = (task_dir / "prompt.md").read_text(encoding="utf-8")
        tests_source = (task_dir / "tests.py").read_text(encoding="utf-8")
        test_tree = ast.parse(tests_source, filename="tests.py")
        tests_total = _test_count(test_tree.body)
        task_results.append(
            _evaluate_task(task_id, prompt, tests_source, tests_total, solve, model)
        )

    generated_results = [
        result for result in task_results if result["status"] != "generation_error"
    ]
    tests_passed = sum(result["tests_passed"] for result in generated_results)
    tests_total = sum(result["tests_total"] for result in generated_results)
    generation_errors = sum(
        result["status"] == "generation_error" for result in task_results
    )
    generated_pass_rate = tests_passed / tests_total if tests_total else 0.0
    result_data = {
        "iteration": iteration,
        "tasks": str(tasks),
        "set": task_set,
        "scaffold": scaffold_file.name,
        "scaffold_sha256": hashlib.sha256(scaffold_file.read_bytes()).hexdigest(),
        "tasks_evaluated": len(task_results),
        "tests_passed": tests_passed,
        "tests_total": tests_total,
        "pass_rate": generated_pass_rate,
        "pass_rate_generated": generated_pass_rate,
        "generation_error_tasks": generation_errors,
        "generation_errors": generation_errors,
        "model": model,
        "task_results": task_results,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    output_path = _result_path(iteration, tasks_path, task_set, model)
    output_path.write_text(json.dumps(result_data, indent=2) + "\n", encoding="utf-8")
    return result_data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", dest="task_set", choices=("optimization", "heldout"), required=True)
    parser.add_argument("--iter", dest="iteration", type=int, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--model", default=None, help="Solver model, e.g. gpt-5.6-luna")
    parser.add_argument("--tasks", default="tasks", help="Task folder, e.g. tasks_v2")
    parser.add_argument("--scaffold", default="scaffold.py", help="Scaffold Python file")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 0:
        parser.error("--limit must be nonnegative")

    result_data = evaluate_set(
        tasks=args.tasks,
        task_set=args.task_set,
        iteration=args.iteration,
        model=args.model,
        scaffold_path=args.scaffold,
        limit=args.limit,
    )
    output_path = _result_path(args.iteration, args.tasks, args.task_set, args.model)
    print(f"Saved results to {output_path.relative_to(ROOT)}")
    tests_passed = result_data["tests_passed"]
    tests_total = result_data["tests_total"]
    generated_pass_rate = result_data["pass_rate_generated"]
    generation_errors = result_data["generation_error_tasks"]
    print(
        "Generated-solution pass rate: "
        f"{tests_passed}/{tests_total} ({generated_pass_rate:.1%}); "
        f"generation errors: {generation_errors}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
