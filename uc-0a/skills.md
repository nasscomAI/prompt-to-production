# Skills — UC-0A: Complaint Classifier

## 1. classify_complaint

**name**
classify_complaint

**description**
Classifies a single complaint description into one of the allowed UC-0A categories, assigns a priority level, provides a one-sentence reason grounded in the complaint's own wording, and flags the result for human review when the classification is genuinely ambiguous. This is the core per-row classification logic used by `batch_classify`.

**input**
- A single complaint row/description (plain text, or a row object containing at minimum a complaint description field).
- No other context is used — classification must be based solely on the content of that one complaint.

**output**
A structured result containing exactly these fields:
- `category` — one of the allowed UC-0A categories only. No invented or free-text categories are permitted. If the correct category cannot be determined with confidence, `category` must be set to `Other`.
- `priority` — one of exactly three values: `Urgent`, `Standard`, or `Low`.
  - `Urgent` is mandatory whenever any required severity keyword appears in the complaint text (case-insensitive): `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`.
  - `Standard` and `Low` are assigned based on the complaint's apparent severity/impact when no required severity keyword is present.
- `reason` — exactly one sentence, citing specific word(s) or phrase(s) drawn directly from the complaint text that justify the assigned category and priority.
- `flag` — `NEEDS_REVIEW` if the complaint is genuinely ambiguous (e.g., category unclear, conflicting signals, insufficient information), otherwise left blank.
  - Whenever `category` is set to `Other` because confidence is insufficient, `flag` must be `NEEDS_REVIEW`.

**error_handling**
- If the input row/description is empty, missing, or unreadable, return `category = Other`, `priority = Low` (unless a severity keyword is present, in which case `priority = Urgent`), `reason` stating that the complaint text was missing or unreadable, and `flag = NEEDS_REVIEW`.
- If the complaint text does not match any allowed category with confidence, return `category = Other` and `flag = NEEDS_REVIEW` — never fabricate or guess a category outside the allowed list.
- If a required severity keyword is present, `priority` must always be set to `Urgent`, regardless of any other signal in the complaint — this rule overrides all other priority reasoning.
- Never invent facts, details, or context not present in the complaint text; `reason` must only cite words actually found in the input.
- If multiple categories seem plausible and none is clearly dominant, do not guess — return `Other` with `NEEDS_REVIEW`.

---

## 2. batch_classify

**name**
batch_classify

**description**
Applies `classify_complaint` to every row of an input CSV of complaint descriptions and produces an output CSV containing the original data plus the required classification fields, applying the same rules identically and consistently across all rows.

**input**
- An input CSV file containing complaint descriptions (one complaint per row), matching the UC-0A input schema.

**output**
- An output CSV file that:
  - Preserves all original input columns.
  - Adds the required classification columns for every row: `category`, `priority`, `reason`, `flag`.
  - Contains one output row per input row — no rows added, removed, merged, or reordered.
  - Uses only the allowed UC-0A categories and the three defined priority values, with no invented categories, fields, or schema changes.

**error_handling**
- Each row is classified independently via `classify_complaint`; a failure or ambiguity on one row must not stop processing of the remaining rows.
- If a row is malformed, empty, or missing the complaint description field, still emit an output row for it with `category = Other`, `flag = NEEDS_REVIEW`, and a `reason` noting the missing/invalid data — do not silently drop rows.
- If the input CSV is missing entirely, unreadable, or missing the expected description column, halt and report the error clearly rather than producing a partial or guessed output file.
- The same classification rules (including the mandatory `Urgent` severity-keyword rule and the `Other` + `NEEDS_REVIEW` fallback for low-confidence cases) must be applied identically to every row — no row-specific rule deviations.
- The output schema must never be altered, reordered in meaning, or extended with unrequested fields; only the four required classification columns are added to the original schema.
