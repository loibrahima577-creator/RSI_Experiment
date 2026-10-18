"""General task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str, model=None) -> str:
    request = (
        "Implement the Python function described in the task. Return only the "
        "complete function code, without explanation or Markdown fences. Match "
        "the requested function name and parameters, and treat the wording and "
        "examples as the specification.\n\n"
        "Implementation guidance:\n"
        "- Match the requested return shape exactly. Use tuples for sequence "
        "results unless the task explicitly requires another type. Examples "
        "that call list(...) do not require a generator; use one only when an "
        "iterator or streaming result is requested.\n"
        "- Unless the task specifies otherwise, return None for empty top-level "
        "input. Check this before building a naturally empty result. For "
        "nonempty input with no matches, return an empty collection when the "
        "result is collection-valued.\n"
        "- Preserve input order and stable ties unless the task specifies "
        "otherwise. When text matching or grouping does not specify case "
        "sensitivity, use case-insensitive normalization such as casefold(). "
        "Apply string methods only to strings. Retain original values and "
        "spellings when required; use normalized keys for grouping categories "
        "when appropriate.\n"
        "- Use deterministic sort keys when values may not be mutually "
        "comparable. Validate stated membership and structural requirements "
        "before trivial early returns. When the task distinguishes invalid or "
        "unknown inputs from valid queries with no result, preserve that "
        "distinction rather than returning a partial result or ordinary "
        "no-result value.\n"
        "- For integer-valued parameters, avoid rejecting compatible "
        "integer-like values solely because they are not built-in ints; use "
        "the relevant Python numeric or index protocol when appropriate, and "
        "enforce stated value constraints.\n"
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