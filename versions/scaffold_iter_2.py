"""General task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str, model=None) -> str:
    request = (
        "Implement the Python function described in the task. Return only the "
        "complete function code, without explanation or Markdown fences. Match "
        "the requested function name and parameters, and treat the wording and "
        "examples as the specification.\n\n"
        "Implementation guidance:\n"
        "- Match the expected return shape exactly, including type, nesting, "
        "and ordering. For sequence-valued results, prefer tuples unless the "
        "task explicitly requires another type. When group order matters, use "
        "an ordered sequence of key/value pairs unless a mapping is requested.\n"
        "- If the overall input is empty and no empty-input result is specified, "
        "return None when there is no meaningful result. Distinguish that from "
        "a nonempty input producing no matches, which should usually yield an "
        "empty collection when the result is collection-valued.\n"
        "- Preserve input order and stable ties unless the task specifies a "
        "different ordering. Normalize comparison or grouping keys when "
        "appropriate, while preserving original input values.\n"
        "- Do not add defensive type checks or rejection rules beyond those "
        "required by the task. Distinguish invalid or unknown inputs from valid "
        "queries that simply have no result when the task semantics call for it.\n\n"
        f"{task_prompt}"
    )
    response = call_llm(request, model=model)
    lines = response.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines).strip()