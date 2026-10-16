"""Baseline task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str) -> str:
    request = (
        "Implement the Python function described below. Return only the Python "
        "function code, without explanation.\n\n"
        f"{task_prompt}"
    )
    response = call_llm(request)
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
    return "\n".join(lines).strip()
