----
name: quick-review
description: Do a quick Python code review for bare except clauses, missing type hints, and unclear variable names. Use when asked for a quick review.
---

# Quick Review

Review the requested Python file without changing it. Keep the review focused on
these three checks; do not report unrelated style, correctness, or security
issues.

## Checklist

1. **Bare `except` clauses** — Find `except:` clauses that catch every
   exception without naming an exception type. Report each location.
2. **Missing type hints** — Check function and method parameters and return
   values for annotations. Report missing annotations, including a missing
   return annotation when a function intentionally returns nothing (use
   `-> None`).
3. **Unclear variable names** — Identify names that make their purpose hard to
   understand, such as vague abbreviations or single-letter names outside
   conventional short-lived loop indices. Include a clearer alternative.

Base findings on the file's actual contents. Include line numbers for findings,
and do not flag an item merely because it could be renamed or annotated
differently. Mark each checklist item as **PASS** or **FINDING**. If a file
cannot be found or read, say so instead of guessing.

## Output

Use this concise format:

```text
## Quick Review: [filename]
- [PASS/FINDING] Bare except clauses: [result]
- [PASS/FINDING] Missing type hints: [result]
- [PASS/FINDING] Unclear variable names: [result]

Summary: [number] finding(s).
```
 
 