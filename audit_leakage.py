"""Audit held-out benchmark text against experiment artifacts without API access."""

import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPLIT_PATH = ROOT / "tasks_v2" / "split.json"
ARTIFACT_GLOBS = (
    (ROOT / "logs", "improver_iter_*.txt"),
    (ROOT / "versions", "scaffold_iter_*.py"),
    (ROOT / "versions", "rejected_iter_*.py"),
)
FUNCTION_PATTERN = re.compile(
    r"\b(?:implement|write|define)\s+(?:the\s+)?(?:function\s+)?"
    r"[`*]*([A-Za-z_]\w*)[`*]*\s*\(",
    re.IGNORECASE,
)


def _add_indicator(indicators, task_id, kind, text, origin):
    key = (task_id, kind, text)
    indicators.setdefault(key, []).append(origin)


def _function_names(prompt_text, tests_text):
    names = {}
    for name in FUNCTION_PATTERN.findall(prompt_text):
        names.setdefault(name, []).append("prompt.md")
    try:
        tree = ast.parse(tests_text)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "solution":
            for alias in node.names:
                if alias.name != "*":
                    names.setdefault(alias.name, []).append("tests.py")
    return names


def _line_match(needle, haystack_line):
    if needle[1] == "function":
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_]){re.escape(needle[2])}(?![A-Za-z0-9_])"
        )
        return pattern.search(haystack_line) is not None
    return needle[2] in haystack_line


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _keyword_value(call, keyword):
    for item in call.keywords:
        if item.arg == keyword:
            return item.value
    return None


def _is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


def _check_failure_provenance(run_loop_source, improve_source):
    checks = []
    try:
        run_tree = ast.parse(run_loop_source, filename="run_loop.py")
        improve_tree = ast.parse(improve_source, filename="improve.py")
    except SyntaxError as exc:
        return [(False, f"could not parse source: {exc}")]

    definitions = {
        node.name: node
        for node in run_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    current_result = definitions.get("_current_result")
    collect_failures = definitions.get("_collect_failures")
    run_function = definitions.get("run")

    current_result_calls = [
        node for node in ast.walk(current_result) if isinstance(node, ast.Call)
    ] if current_result else []
    checks.append((
        any(
            _call_name(node.func) == "evaluate._result_path"
            and len(node.args) >= 3
            and isinstance(node.args[2], ast.Constant)
            and node.args[2].value == "optimization"
            for node in current_result_calls
        ),
        "_current_result reads the optimization result file",
    ))

    prior_assignments = []
    run_calls = list(ast.walk(run_function)) if run_function else []
    if run_function:
        for node in ast.walk(run_function):
            if isinstance(node, ast.Assign) and any(
                _is_name(target, "prior_result") for target in node.targets
            ):
                prior_assignments.append(node.value)
            elif isinstance(node, ast.AnnAssign) and _is_name(node.target, "prior_result"):
                prior_assignments.append(node.value)
    prior_sources_ok = len(prior_assignments) == 2
    saw_optimization_fallback = False
    saw_current_result = False
    for value in prior_assignments:
        if isinstance(value, ast.Call) and _call_name(value.func) == "_current_result":
            saw_current_result = True
        elif isinstance(value, ast.Call) and _call_name(value.func) == "evaluate.evaluate_set":
            task_set = _keyword_value(value, "task_set")
            if isinstance(task_set, ast.Constant) and task_set.value == "optimization":
                saw_optimization_fallback = True
            else:
                prior_sources_ok = False
        else:
            prior_sources_ok = False
    checks.append((
        prior_sources_ok and saw_current_result and saw_optimization_fallback,
        "run() sources prior_result only from the optimization result path or an optimization evaluation",
    ))

    collect_calls = [
        node for node in run_calls
        if isinstance(node, ast.Call) and _call_name(node.func) == "_collect_failures"
    ]
    checks.append((
        len(collect_calls) == 1
        and bool(collect_calls[0].args)
        and _is_name(collect_calls[0].args[0], "prior_result"),
        "run() builds failures from prior_result only",
    ))

    collects_task_results = False
    if collect_failures:
        collects_task_results = any(
            isinstance(node, ast.For)
            and isinstance(node.iter, ast.Subscript)
            and _is_name(node.iter.value, "result")
            and isinstance(node.iter.slice, ast.Constant)
            and node.iter.slice.value == "task_results"
            for node in ast.walk(collect_failures)
        ) and any(
            isinstance(node, ast.Call)
            and _call_name(node.func) == "failures.append"
            for node in ast.walk(collect_failures)
        )
    checks.append((
        collects_task_results,
        "_collect_failures builds its list from the supplied result's task_results",
    ))

    improve_calls = [
        node for node in run_calls
        if isinstance(node, ast.Call) and _call_name(node.func) == "improver.improve"
    ]
    checks.append((
        len(improve_calls) == 1
        and len(improve_calls[0].args) >= 2
        and _is_name(improve_calls[0].args[1], "failures"),
        "run() passes that failures list to improver.improve",
    ))

    failures_assignments = []
    if run_function:
        for node in ast.walk(run_function):
            if isinstance(node, ast.Assign) and any(
                _is_name(target, "failures") for target in node.targets
            ):
                failures_assignments.append(node.value)
            elif isinstance(node, ast.AnnAssign) and _is_name(node.target, "failures"):
                failures_assignments.append(node.value)
    checks.append((
        len(failures_assignments) == 1
        and isinstance(failures_assignments[0], ast.Call)
        and _call_name(failures_assignments[0].func) == "_collect_failures",
        "run() has exactly one failures-list assignment, via _collect_failures",
    ))

    improve_defs = {
        node.name: node
        for node in improve_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    build_prompt = improve_defs.get("build_prompt")
    improve_function = improve_defs.get("improve")
    prompt_uses_failures = False
    if build_prompt:
        prompt_uses_failures = any(
            isinstance(node, ast.For) and _is_name(node.iter, "failures")
            for node in ast.walk(build_prompt)
        ) and any(
            isinstance(node, ast.Call)
            and _call_name(node.func).endswith("append")
            and node.args
            and isinstance(node.args[0], ast.Dict)
            for node in ast.walk(build_prompt)
        )
    checks.append((prompt_uses_failures, "improve.build_prompt formats records from its failures argument"))

    build_prompt_calls = [
        node for node in ast.walk(improve_function) if isinstance(node, ast.Call)
    ] if improve_function else []
    checks.append((
        any(
            _call_name(node.func) == "build_prompt"
            and len(node.args) >= 2
            and _is_name(node.args[1], "failures")
            for node in build_prompt_calls
        ),
        "improve.improve passes its failures argument to build_prompt",
    ))
    return checks


def _relevant_source_lines(filename, source, keywords):
    selected = []
    for number, line in enumerate(source.splitlines(), start=1):
        if any(keyword in line for keyword in keywords):
            selected.append(f"{filename}:{number}: {line}")
    return selected


def main():
    report = ["Held-out leakage audit", "======================", ""]
    failures = []
    indicators = {}
    held_out = []

    try:
        split_data = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
        held_out = split_data["held_out_set"]
        if not isinstance(held_out, list) or not held_out:
            raise ValueError("held_out_set must be a non-empty list")
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        failures.append(f"Could not read held-out task list: {exc}")
        held_out = []

    report.append(f"Held-out tasks: {', '.join(held_out) if held_out else '(none)'}")
    for task_id in held_out:
        task_dir = ROOT / "tasks_v2" / task_id
        prompt_path = task_dir / "prompt.md"
        tests_path = task_dir / "tests.py"
        try:
            prompt_text = prompt_path.read_text(encoding="utf-8")
            tests_text = tests_path.read_text(encoding="utf-8")
        except OSError as exc:
            failures.append(f"{task_id}: unable to read prompt.md/tests.py: {exc}")
            continue

        names = _function_names(prompt_text, tests_text)
        if not names:
            failures.append(f"{task_id}: no requested function name found")
        for name in sorted(names):
            for source_name in names[name]:
                origin = f"{task_id}/{source_name} function name"
                _add_indicator(indicators, task_id, "function", name, origin)

        for filename, source in (("prompt.md", prompt_text), ("tests.py", tests_text)):
            for line_number, raw_line in enumerate(source.splitlines(), start=1):
                line = raw_line.strip()
                if len(line) >= 20:
                    _add_indicator(
                        indicators,
                        task_id,
                        "line",
                        line,
                        f"{task_id}/{filename}:{line_number}",
                    )

    report.extend(["", "Extracted indicators", "---------------------"])
    report.append(f"Function names: {sum(key[1] == 'function' for key in indicators)}")
    report.append(f"Distinct lines (20+ characters): {sum(key[1] == 'line' for key in indicators)}")
    for (task_id, kind, text), origins in sorted(indicators.items()):
        label = "function" if kind == "function" else "line"
        report.append(f"{task_id} [{label}] {text!r} (from {', '.join(origins)})")

    targets = []
    for directory, pattern in ARTIFACT_GLOBS:
        if directory.exists():
            targets.extend(sorted(directory.glob(pattern)))
    targets = sorted(set(targets))
    if not targets:
        failures.append("No matching logs or version artifacts were found to scan")

    report.extend(["", "Artifact search", "----------------"])
    report.append(f"Files scanned: {len(targets)}")
    match_count = 0
    for target in targets:
        try:
            target_lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            failures.append(f"Unable to scan {target.relative_to(ROOT)}: {exc}")
            continue
        for indicator in sorted(indicators):
            task_id, kind, text = indicator
            for line_number, target_line in enumerate(target_lines, start=1):
                if _line_match(indicator, target_line):
                    match_count += 1
                    origins = ", ".join(indicators[indicator])
                    report.append(
                        f"MATCH {target.relative_to(ROOT)}:{line_number}: "
                        f"{kind} {text!r} from {origins}; artifact line: {target_line.strip()}"
                    )
    if match_count == 0:
        report.append("No held-out function names or extracted lines matched the scanned artifacts.")
    else:
        failures.append(f"Found {match_count} held-out indicator match(es)")

    run_loop_path = ROOT / "run_loop.py"
    improve_path = ROOT / "improve.py"
    try:
        run_loop_source = run_loop_path.read_text(encoding="utf-8")
        improve_source = improve_path.read_text(encoding="utf-8")
    except OSError as exc:
        run_loop_source = improve_source = ""
        failures.append(f"Could not read improve.py/run_loop.py: {exc}")

    report.extend(["", "Failures-list provenance check", "-------------------------------"])
    checks = _check_failure_provenance(run_loop_source, improve_source)
    for passed, message in checks:
        report.append(f"{'PASS' if passed else 'FAIL'}: {message}")
        if not passed:
            failures.append(message)

    report.extend(["", "Relevant code lines", "-------------------"])
    for filename, source, keywords in (
        (
            "run_loop.py",
            run_loop_source,
            (
                "def _current_result", "evaluate._result_path", 'result.get("set")',
                "def _collect_failures", 'result["task_results"]', "failures = _collect_failures",
                "failures.append", "prior_result =", 'task_set="optimization"',
                'task_set="heldout"', "improver.improve",
            ),
        ),
        (
            "improve.py",
            improve_source,
            (
                "def build_prompt", "limited_failures", "for failure in failures",
                "limited_failures.append", "optimization-set failures", "def improve",
                "build_prompt(scaffold_source, failures)",
            ),
        ),
    ):
        report.extend(_relevant_source_lines(filename, source, keywords))

    report.extend(["", "", f"{'FAIL' if failures else 'PASS'}"])
    if failures:
        report.append("Reasons:")
        report.extend(f"- {reason}" for reason in failures)
    final_report = "\n".join(report) + "\n"
    output_path = ROOT / "results" / "leakage_audit.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_report, encoding="utf-8")
    print(final_report, end="")
    print(f"Report saved to {output_path.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
