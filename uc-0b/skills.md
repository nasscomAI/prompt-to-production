# Skills — UC-0B Summary That Changes Meaning

## retrieve_policy
**Input:** `input_path` — path to a .txt policy file
**Output:** dict mapping clause number (e.g. "5.2") to that clause's full text
**Behavior:**
- Parses the document line by line, detecting clause headers via the
  pattern `N.N <text>` (e.g. "5.2 LWP requires approval...").
- Accumulates wrapped continuation lines into the same clause until
  the next clause number or a section divider/header is hit.
- Returns a flat dict of clause number -> full clause text, with
  nothing paraphrased or trimmed at this stage.

## summarize_policy
**Input:** the structured sections dict from retrieve_policy
**Output:** a string summary with one block per target clause
**Behavior:**
- Iterates the fixed ground-truth clause list (2.3, 2.4, 2.5, 2.6,
  2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
- For each clause present, outputs "[Clause N.N] <verbatim text>" -
  no paraphrasing, so multi-condition clauses cannot lose a condition.
- Any target clause missing from the source is explicitly listed under
  a [FLAG] line rather than silently dropped.
