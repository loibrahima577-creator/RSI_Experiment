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
        "- Translate stated preconditions into checks before processing. For "
        "example, do not let zip silently truncate inputs described as equally "
        "sized. Distinguish invalid or unknown inputs from valid queries with "
        "no result; for graph queries, distinguish unknown nodes from known "
        "but unreachable nodes. Check these conditions before trivial early "
        "returns.\n"
        "- Preserve input order and stable ties unless the task specifies "
        "otherwise. For grouping, preserve first-seen group order and use the "
        "requested representation; use an ordered sequence of key/group pairs "
        "when the task describes ordered groups rather than a mapping. When "
        "text matching or grouping does not specify case sensitivity, use "
        "case-insensitive normalization such as casefold(). Retain original "
        "values and spellings when required, and apply string methods only to "
        "strings.\n"
        "- Respect types implied by the operation: for example, alphabetical "
        "labels and substring queries are textual, and integer-valued "
        "parameters require an integer or compatible index value. Do not "
        "silently broaden accepted types with coercions or fallback sort keys. "
        "Use the relevant Python numeric or index protocol when appropriate, "
        "enforce stated value constraints, and follow any specified invalid-"
        "input behavior.\n"
        "- Use deterministic sort keys when values may not be mutually "
        "comparable. Do not add defensive checks or rejection rules beyond "
        "the task's stated or clearly implied requirements.\n\n"
        f"{task_prompt}"
    )
    response = call_llm(request, model=model)
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines).strip()