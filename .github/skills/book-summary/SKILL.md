---
name: book-summary
description: Generate a formatted Markdown summary of a book collection from JSON data or a list of books. Use when asked to summarize books, a book collection, or collection data.
---

# Book Summary

When given book collection data, summarize every book in a clear Markdown
table. Read the provided data and do not invent missing details.

## Formatting Rules

- Start with the heading `## Book Collection Summary`.
- Include a Markdown table with these columns in this order: **Title**,
  **Author**, **Year**, **Read Status**.
- Sort by publication year from oldest to newest. Put books with an unknown or
  invalid year after books with a known year; keep their original order among
  themselves.
- Show a missing author as `Unknown`. Treat a missing, invalid, or non-positive
  year as `Unknown`.
- Show read status as `✅ Read` when `read` is `true` and `❌ Unread` when it is
  `false` or missing.
- Include every book, including entries with incomplete information.
- After the table, report the total number of books, the number read, and the
  number unread.
- If the data cannot be read or does not contain a recognizable book
  collection, explain the problem instead of guessing.

## Output Example

```markdown
## Book Collection Summary

| Title | Author | Year | Read Status |
|---|---|---:|---|
| Example Book | Example Author | 2000 | ✅ Read |

**Total:** 1 book — 1 read, 0 unread.
```
