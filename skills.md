# Skills: Policy Summary Integrity Agent

---

## Skill 1 — `read_policy_document`
**Purpose:** Load and pre-process a plain-text policy document.

**Input:** File path to a `.txt` policy document.

**Steps:**
1. Read the file with UTF-8 encoding.
2. Split into sections by detecting headings (ALL CAPS lines, numbered sections, or lines
   ending with a colon).
3. Number each clause for cross-referencing in the summary.

**Output:** Structured list of `{clause_id, heading, body}` objects.

---

## Skill 2 — `summarise_policy`
**Purpose:** Generate a faithful summary of the policy document.

**Input:** Structured clause list from `read_policy_document`.

**Prompt rules:**
- System prompt instructs the model to cover every clause.
- Explicitly forbids merging clauses with different conditions.
- Requires numerical limits (days, amounts) to be copied exactly.
- Requires modal verbs ("must", "shall", "may", "cannot") to match the source.

**Output:** Summary text string.

---

## Skill 3 — `detect_meaning_change`
**Purpose:** Compare the source document against the generated summary and flag
clauses where meaning has changed, been omitted, or been distorted.

**Input:** Original text + summary text.

**Detection rules:**
- OMISSION: A clause present in source but absent in summary.
- SOFTENING: Source says "must" but summary says "may" or "can".
- CAP LOSS: Source states a numerical limit; summary omits or changes it.
- CONDITION LOSS: Source has an eligibility condition; summary drops it.
- INVERSION: Summary implies the opposite of the source.

**Output:** List of `{clause_id, issue_type, source_text, summary_text, risk_level}`.

---

## Skill 4 — `write_summary_file`
**Purpose:** Write the final, verified summary to a `.txt` output file.

**Input:** Summary text + list of flagged issues.

**Steps:**
1. Write the summary.
2. Append a `[REVIEW FLAGS]` section listing any detected meaning-change issues.
3. Save to `summary_hr_leave.txt` (or the appropriate policy output file).

**Output:** Written file on disk.
