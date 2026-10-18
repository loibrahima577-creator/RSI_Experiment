"""General task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str, model=None) -> str:
    request = (
        "Implement the Python function described in the task. Return only the "
        "complete function code, without explanation or Markdown fences. Match "
        "the requested function name and parameters, and treat the wording and "
        "examples as the specification.\n\n"
        "Implementation guidance:\n"
        "- Match the expected return shape exactly. Use tuples for sequence "
        "results unless the task explicitly requires another type. Examples "
        "that call list(...) do not require a generator; use one only when an "
        "iterator or streaming result is requested.\n"
        "- Unless the task specifies otherwise, return None for empty top-level "
        "input. For nonempty input with no matches, return an empty collection "
        "when the result is collection-valued.\n"
        "- Preserve input order and stable ties unless the task specifies "
        "otherwise. Normalize text comparison or grouping keys when appropriate "
        "while retaining original values; for equivalent labels, keep the first "
        "spelling encountered. Use deterministic sort keys when raw values may "
        "not be mutually comparable.\n"
        "- Enforce stated input constraints. Where task semantics distinguish "
        "invalid or unknown inputs from valid queries with no result, fail for "
        "the former rather than treating them as ordinary no-result cases. "
        "Detect violated structural requirements rather than returning a "
        "partial or invalid result.\n"
        "- Do not add defensive checks or rejection rules beyond the task's "
        "stated requirements.\n\n"
        f"{task_prompt}"
    )
    response = call_llm(request, model=model)
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines).strip()