"""Ask an LLM to improve the experiment scaffold from optimization failures."""

import json

from llm import call_llm


LAST_PROMPT = ""
LAST_RESPONSE = ""


def _trim(value, limit: int = 1500) -> str:
    return str(value)[:limit]


def build_prompt(scaffold_source: str, failures) -> str:
    limited_failures = []
    for failure in failures:
        limited_failures.append({
            "task_prompt": _trim(failure.get("task_prompt", "")),
            "generated_solution": _trim(failure.get("generated_solution", "")),
            "failing_assertion_messages": [
                _trim(message)
                for message in failure.get("failing_assertion_messages", [])
            ],
        })
    return (
        "Improve the scaffold in a general way using only the optimization-set "
        "failures below. Do not add task-specific hacks, hard-coded task ids, "
        "or hard-coded task answers. Keep the scaffold small and preserve its "
        "public interface.\n\n"
        "Contract: define solve(task_prompt: str, model=None) -> str. It must "
        "return Python code for the function requested by task_prompt and make "
        "LLM calls only through `from llm import call_llm`.\n\n"
        "Current scaffold source:\n"
        "```python\n"
        f"{scaffold_source}\n"
        "```\n\n"
        "Optimization-set failures (each field is limited to 1500 characters):\n"
        f"{json.dumps(limited_failures, indent=2, ensure_ascii=False)}\n\n"
        "Return the complete replacement scaffold source, without commentary."
    )


def _strip_fence(response: str) -> str:
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
    return "\n".join(lines).strip()


def improve(scaffold_source, failures, model="gpt-6.1-sol") -> str:
    """Return an improved full scaffold; retain the prompt and raw reply for logs."""
    global LAST_PROMPT, LAST_RESPONSE
    LAST_PROMPT = build_prompt(scaffold_source, failures)
    LAST_RESPONSE = call_llm(LAST_PROMPT, effort="high", model=model)
    return _strip_fence(LAST_RESPONSE)
