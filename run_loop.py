"""Run successive scaffold improvements using optimization-set feedback."""

import argparse
import ast
import csv
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

import evaluate
import improve as improver


ROOT = Path(__file__).resolve().parent
VERSIONS_DIR = ROOT / "versions"
RESULTS_DIR = ROOT / "results"
LOGS_DIR = ROOT / "logs"
ALLOWED_IMPORTS = {"re", "json", "textwrap", "typing"}
FORBIDDEN_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "os", "sys",
    "subprocess", "socket", "pathlib", "shutil",
}


def _annotation_is_str(annotation) -> bool:
    return isinstance(annotation, ast.Name) and annotation.id == "str"


def check_scaffold(source: str) -> tuple[bool, str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, f"syntax error: {exc.msg}"

    imported_call_llm = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ALLOWED_IMPORTS or alias.asname in FORBIDDEN_NAMES:
                    return False, f"disallowed import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0:
                return False, "relative imports are disallowed"
            if node.module == "llm" and [item.name for item in node.names] == ["call_llm"]:
                if node.names[0].asname is not None:
                    return False, "call_llm import alias is disallowed"
                imported_call_llm = True
            else:
                return False, f"disallowed import: {node.module}"
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            return False, f"forbidden name: {node.id}"
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
            return False, f"forbidden attribute: {node.attr}"
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "auth.json" in node.value.lower():
                return False, "forbidden credential-file string"

    if not imported_call_llm:
        return False, "must import call_llm from llm"
    solve_defs = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "solve"
    ]
    if len(solve_defs) != 1 or isinstance(solve_defs[0], ast.AsyncFunctionDef):
        return False, "must define one synchronous solve function"
    solve = solve_defs[0]
    args = solve.args
    if (
        args.posonlyargs
        or [arg.arg for arg in args.args] != ["task_prompt", "model"]
        or args.vararg is not None
        or args.kwarg is not None
        or args.kwonlyargs
        or len(args.defaults) != 1
        or not isinstance(args.defaults[0], ast.Constant)
        or args.defaults[0].value is not None
        or not _annotation_is_str(args.args[0].annotation)
        or not _annotation_is_str(solve.returns)
    ):
        return False, "solve must have signature solve(task_prompt: str, model=None) -> str"
    if not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "call_llm"
        for node in ast.walk(solve)
    ):
        return False, "solve must call call_llm"
    return True, "accepted"


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _current_result(iteration: int, tasks: str, model: str, scaffold_path: Path) -> dict | None:
    result_path = evaluate._result_path(iteration, tasks, "optimization", model)
    if not result_path.exists():
        return None
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if (
        result.get("scaffold_sha256") not in (None, _hash_file(scaffold_path))
        or result.get("iteration") != iteration
        or result.get("tasks") != str(tasks)
        or result.get("set") != "optimization"
        or result.get("model") != model
        or result.get("scaffold") != scaffold_path.name
    ):
        return None
    if any(
        item.get("status") not in ("passed", "generation_error")
        and "generated_solution" not in item
        for item in result.get("task_results", [])
    ):
        return None
    return result


def _collect_failures(result: dict, tasks: str) -> list[dict]:
    tasks_dir = Path(tasks)
    if not tasks_dir.is_absolute():
        tasks_dir = ROOT / tasks_dir
    failures = []
    for task_result in result["task_results"]:
        if task_result.get("status") == "passed":
            continue
        task_prompt = (tasks_dir / task_result["task_id"] / "prompt.md").read_text(
            encoding="utf-8"
        )
        failures.append({
            "task_prompt": task_prompt[:1500],
            "generated_solution": str(task_result.get("generated_solution", ""))[:1500],
            "failing_assertion_messages": [
                str(message)[:1500]
                for message in task_result.get("failing_assertions", [])
            ] or [
                (
                    f"{task_result.get('error_type', 'generation_error')}: "
                    f"{task_result.get('error_message', 'solution generation failed')}"
                )[:1500]
            ],
        })
    return failures


def _append_summary(iteration: int, optimization_rate: float, heldout_rate: float, accepted: bool):
    path = RESULTS_DIR / "summary_v2.csv"
    path.parent.mkdir(exist_ok=True)
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        if needs_header:
            writer.writerow(("iteration", "optimization_pass_rate", "heldout_pass_rate", "accepted"))
        writer.writerow((iteration, optimization_rate, heldout_rate, str(accepted).lower()))
        stream.flush()
        os.fsync(stream.fileno())


def _progress(message: str) -> None:
    timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def run(tasks: str, model: str, iterations: int, fresh: bool = False) -> bool:
    VERSIONS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    current_path = ROOT / "scaffold.py"

    for iteration in range(1, iterations + 1):
        try:
            next_path = VERSIONS_DIR / f"scaffold_iter_{iteration}.py"
            optimization_path = evaluate._result_path(
                iteration, tasks, "optimization", model
            )
            heldout_path = evaluate._result_path(iteration, tasks, "heldout", model)
            if (
                not fresh
                and next_path.exists()
                and optimization_path.exists()
                and heldout_path.exists()
            ):
                _progress(f"iteration {iteration}: already complete; skipping")
                current_path = next_path
                continue

            prior_iteration = iteration - 1
            prior_result = _current_result(prior_iteration, tasks, model, current_path)
            if prior_result is None:
                prior_result = evaluate.evaluate_set(
                    tasks=tasks,
                    task_set="optimization",
                    iteration=prior_iteration,
                    model=model,
                    scaffold_path=current_path,
                    progress_callback=lambda task_set, number, total: _progress(
                        f"iteration {iteration}: evaluating {task_set} set (task {number}/{total})"
                    ),
                )
            failures = _collect_failures(prior_result, tasks)
            previous_source = current_path.read_text(encoding="utf-8")

            prompt = ""
            raw_response = ""
            candidate = None
            _progress(f"iteration {iteration}: improver call started")
            try:
                candidate = improver.improve(previous_source, failures, model=model)
                prompt = improver.LAST_PROMPT
                raw_response = improver.LAST_RESPONSE
                accepted, reason = check_scaffold(candidate)
            except Exception as exc:
                prompt = improver.LAST_PROMPT
                raw_response = f"Improvement request failed: {type(exc).__name__}: {exc}"
                accepted, reason = False, "improvement request failed"
            _progress(f"iteration {iteration}: improver call finished")

            if accepted:
                next_source = candidate
            else:
                next_source = previous_source
                if candidate is not None:
                    rejected_path = VERSIONS_DIR / f"rejected_iter_{iteration}.py"
                    rejected_path.write_text(candidate, encoding="utf-8")
            next_path.write_text(next_source, encoding="utf-8")
            (LOGS_DIR / f"improver_iter_{iteration}.txt").write_text(
                "IMPROVER PROMPT\n\n"
                + prompt
                + "\n\nRAW RESPONSE\n\n"
                + raw_response
                + f"\n\nSAFETY RESULT: {reason}\n",
                encoding="utf-8",
            )

            progress_callback = lambda task_set, number, total: _progress(
                f"iteration {iteration}: evaluating {task_set} set (task {number}/{total})"
            )
            optimization = evaluate.evaluate_set(
                tasks=tasks,
                task_set="optimization",
                iteration=iteration,
                model=model,
                scaffold_path=next_path,
                progress_callback=progress_callback,
            )
            heldout = evaluate.evaluate_set(
                tasks=tasks,
                task_set="heldout",
                iteration=iteration,
                model=model,
                scaffold_path=next_path,
                progress_callback=progress_callback,
            )
            _append_summary(
                iteration,
                optimization["pass_rate_generated"],
                heldout["pass_rate_generated"],
                accepted,
            )
            current_path = next_path
            _progress(
                f"iteration {iteration} done: optimization "
                f"{optimization['pass_rate_generated']:.2f}, heldout "
                f"{heldout['pass_rate_generated']:.2f}"
            )
        except KeyboardInterrupt:
            _progress(f"iteration {iteration} interrupted by Ctrl+C")
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", default="tasks_v2")
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--iterations", type=int, required=True)
    parser.add_argument(
        "--fresh", action="store_true", help="rerun iterations even when their outputs exist"
    )
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be at least 1")
    return 0 if run(args.tasks, args.model, args.iterations, fresh=args.fresh) else 130


if __name__ == "__main__":
    raise SystemExit(main())
