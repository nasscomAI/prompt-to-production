# UC-0B — skills.md
# Summary That Changes Meaning

---

## Skill: faithful_policy_summariser

### Purpose
Summarise a policy document completely and faithfully — preserving every clause, number, obligation, and prohibition — so that no reader is misled or left uninformed.

### Trigger
Called when the app receives a `.txt` policy document and a request to summarise it.

### Input
- `document_text` (str): Full text of the policy document.
- `document_name` (str): File name or title (e.g., `policy_hr_leave.txt`).

### Output
- A structured plain-language summary grouped by section.
- Every numbered clause represented as its own bullet point.
- All numeric values (days, amounts, percentages, deadlines) preserved exactly.
- Final line: `CLAUSES COVERED: N of N`

---

## Skill Steps

### Step 1 — Clause Extraction
Before writing any summary, scan the document and list every numbered or lettered clause, rule, limit, and condition.
Output this internally as a checklist.

### Step 2 — Section Grouping
Group related clauses under a section heading that matches the document's own headings.

### Step 3 — Plain-Language Translation
Rewrite each clause in plain language. Rules:
- Replace legal terms with everyday equivalents.
- Never change "must" to "may", "shall" to "can", or "prohibited" to "discouraged".
- Never change numeric values.
- If a clause contains a list of conditions, all conditions must appear.

### Step 4 — Completeness Check
Cross-reference the summary against the extracted clause list from Step 1.
Every clause must be present. If any is missing, add it before finalising.

### Step 5 — Output Formatting
```
## [Document Title]

### [Section Name]
- Clause N.N: [plain-language summary of the clause]
- Clause N.N: [plain-language summary of the clause]

### [Section Name]
- ...

CLAUSES COVERED: N of N
```

---

## Common Failure Modes (and how this skill avoids them)

| Failure | How This Skill Prevents It |
|---|---|
| Inflated entitlement ("12 days" instead of "10") | Numeric values copied verbatim from source |
| Softened obligation ("should" instead of "must") | Modal verbs preserved exactly |
| Omitted restriction | Clause extraction checklist in Step 1 forces completeness |
| Merged clauses losing a condition | Each clause gets its own bullet |
| Wrong document summarised | `document_name` tracked and printed in output header |

---

## Example Invocation (Python)

```python
summary = faithful_policy_summariser(
    document_text=open("data/policy-documents/policy_hr_leave.txt").read(),
    document_name="policy_hr_leave.txt"
)
print(summary)
```
