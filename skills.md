# skills.md — UC-0B: Summary That Changes Meaning

## Skill 1 — `summarise_policy`

**Purpose:** Produce a structured, complete summary of a policy document.

**Input:** Raw policy document text (string)

**Output:** A summary that:
- Covers every numbered section/clause
- Preserves mandatory language ("must", "required", "not permitted")
- Retains all eligibility conditions, exceptions, and deadlines
- Is shorter than the original but loses nothing of legal or compliance significance

**Prompt template:**
```
You are a policy summarisation specialist.
Read the policy document below and write a summary.

RULES:
- Cover every numbered clause — do not skip any.
- Preserve mandatory language exactly: if the policy says "must", your summary says "must".
- Include all exceptions, eligibility conditions, deadlines, and penalty clauses.
- Do not add any information not present in the source document.
- Format: use numbered points matching the original clause numbers.

DOCUMENT:
{document_text}

OUTPUT FORMAT:
Summary:
1. <clause 1 summary>
2. <clause 2 summary>
...
```

---

## Skill 2 — `fidelity_check`

**Purpose:** Compare the summary against the original and detect meaning changes.

**Input:** Original policy text + generated summary (both strings)

**Output:** A structured fidelity report listing:
- ✅ Clauses correctly represented
- ⚠️ Clauses weakened or softened
- ❌ Clauses missing from the summary
- 🔴 Clauses where meaning is materially changed

**Prompt template:**
```
You are a compliance auditor checking whether a policy summary is accurate.

Compare the ORIGINAL POLICY against the SUMMARY below.

For each numbered clause in the original:
1. Check if it appears in the summary.
2. Check if the obligation strength is preserved (must → must, not softened to "may").
3. Check if exceptions and conditions are retained.
4. Flag any distortion, omission, or addition.

ORIGINAL POLICY:
{original_text}

SUMMARY:
{summary_text}

OUTPUT FORMAT:
Fidelity Report:
- Clause X: ✅ Correctly represented / ⚠️ Softened / ❌ Missing / 🔴 Meaning changed
  Note: <brief explanation if not ✅>

Overall verdict: PASS / FAIL
Reason: <one sentence>
```

---

## Skill 3 — `load_document`

**Purpose:** Read a `.txt` policy file from disk and return its contents as a string.

**Implementation:** Standard Python `open()` + `read()` — no external dependencies needed.
