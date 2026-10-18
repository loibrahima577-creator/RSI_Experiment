"""General task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str, model=None) -> str:
    request = (
        "Implement the Python function described in the task. Return only the "
        "complete function code, without explanation or Markdown fences. Match "
        "the requested function name and parameters, and use the task wording "
        "and examples as the specification.\n\n"
        "Implementation guidance:\n"
        "- Return concrete values, not generators. For sequence-valued results, "
        "prefer tuples unless the task explicitly requires another type.\n"
        "- Preserve input order and stable ties unless the task specifies a "
        "different ordering.\n"
        "- Handle empty inputs, no matches, unreachable results, and boundary "
        "cases deliberately. Use None when an empty overall input leaves no "
        "meaningful result; use an empty collection for a valid collection "
        "result with no matches.\n"
        "- Validate stated preconditions and reject invalid arguments rather "
        "than silently coercing them.\n"
        "- Unless the task says otherwise, compare text case-insensitively for "
        "matching, grouping, alphabetical ordering, and duplicate detection; "
        "preserve original values and first-occurrence spelling where relevant.\n\n"
        f"{task_prompt}"
    )
    response = call_llm(request, model=model)
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines).strip()