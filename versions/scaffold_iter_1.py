"""Task-solving scaffold."""

from llm import call_llm


def solve(task_prompt: str, model=None) -> str:
    request = f"""
Implement the Python function described in the task below.

Treat the task text, examples, and requested signature as a strict behavioral
contract. Hidden tests check edge cases and exact return values. Reason through
the requirements silently, then return only the complete Python function
definition, with no markdown, explanation, or tests.

Before writing the function, check all of the following:

- Match the requested function name and parameters exactly.
- Infer the exact result shape and container type from the specification and
  examples. Materialize collection results unless laziness is explicitly
  required. When a collection result type is not explicitly specified, use an
  immutable tuple consistently, including nested collections. Return None for
  an empty or unavailable result unless the specification explicitly requires
  an empty collection or another value.
- Handle empty inputs, singleton inputs, ties, repeated values, zero and
  boundary amounts, and already-sorted or already-complete inputs.
- Enforce stated preconditions and reject malformed or incompatible inputs
  instead of silently truncating, dropping, or coercing them. Use a natural
  built-in exception type.
- Preserve input objects and spelling when the result is meant to contain
  original values. For textual matching, grouping, equality, and ordering,
  use case-insensitive comparisons when the wording does not explicitly make
  case significant, while retaining the appropriate original spelling.
- Preserve stable input order when the task does not specify a tie-breaker.
- For graph and ordering tasks, validate referenced nodes, distinguish an
  unreachable result from an invalid input, and ensure every supplied item is
  represented when required.
- Use only the standard library, with imports inside the function if needed.
  Do not hard-code examples, task names, answers, or special cases.

Task:
{task_prompt}
"""
    response = call_llm(request, model=model).strip()

    if "```" in response:
        parts = response.split("```")
        if len(parts) >= 3:
            response = parts[1].strip()
            first_line, separator, remainder = response.partition("\n")
            if first_line.strip().lower() in {"python", "py"}:
                response = remainder if separator else ""

    return response.strip()