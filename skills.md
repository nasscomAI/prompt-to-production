# skills.md — UC-0B: Summary That Changes Meaning

> Participant: Hyderabad Submission

---

## Skill 1 — `read_policy_document`

**What it does:** Reads a plain-text policy document from disk and returns its full content.

**Input:** File path to a `.txt` policy document.

**Output:** Raw string content of the file.

**Why it's a separate skill:**
Isolating file I/O means we can swap in a PDF reader, a database fetch, or an API
call later without touching the summarization logic.

**Error handling:**
- If file not found → print clear error with fix hint, exit with code 1.
- If file is empty → warn and exit gracefully.

---

## Skill 2 — `summarize_without_drift`

**What it does:** Calls the Claude API with a strict system prompt to produce a
structured summary that preserves all clauses, numbers, and conditions.

**Input:** Raw policy text string.

**Output:** Structured plain-text summary string.

**Key prompt constraints enforced:**
1. Every numbered clause must appear — no omissions.
2. Numbers (days, amounts, %) preserved exactly.
3. Modal verbs preserved as written (entitled/must/may/shall).
4. Conditions (e.g. "subject to approval") kept intact.
5. No advice, interpretation, or inference added.
6. Distinct clause types (e.g. earned leave vs medical leave) never merged.

**Failure modes actively prevented:**
- Meaning softening: "entitled to" → "can"
- Number rounding: "21 days" → "about 3 weeks"
- Silent clause omission: penalty/encashment clauses dropped
- Condition stripping: "only if approved" removed

---

## Skill 3 — `validate_summary` (CRAFT loop)

**What it does:** Runs automated checks comparing the original document and the
generated summary to catch common drift patterns before the file is written.

**Checks performed:**
- Rounding language detector: flags "about", "approximately", "roughly", "around"
- Number preservation check: finds numbers in original missing from summary
- (Future) Clause count comparison: counts numbered clauses in both

**Input:** Original text + summary text.

**Output:** List of warning strings. Empty list = passed.

**Why it matters:**
This closes the CRAFT loop programmatically — rather than relying solely on human
review, the script self-checks before saving output.

---

## Skill 4 — `write_summary_file`

**What it does:** Writes the validated summary to a `.txt` output file, naming it
`summary_<policy_name>.txt` automatically derived from the input filename.

**Input:** Summary string + output file path.

**Output:** File on disk; prints confirmation path to console.

---

## Skill Composition (how they connect)

```
read_policy_document(path)
        ↓
summarize_without_drift(policy_text)
        ↓
validate_summary(original, summary)   ← CRAFT loop gate
        ↓
write_summary_file(summary, output_path)
```

Each skill is a single Python function in `app.py`, making the pipeline easy to
test, debug, and extend independently.
