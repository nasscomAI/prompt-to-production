# UC-0B — HR Leave Policy Skills

## Skill: retrieve_policy

### Purpose
Load the HR leave policy text file and return its contents as structured numbered sections.

### Input
A `.txt` policy file.

Expected source:

`../data/policy-documents/policy_hr_leave.txt`

### Process

1. Read the complete policy file.
2. Preserve every numbered section and subsection.
3. Identify section and clause numbers exactly as written.
4. Do not omit clauses.
5. Do not add information that is not present in the source.
6. Preserve all conditions, exceptions, deadlines, limits, approvers, and prohibitions.
7. Treat the source policy as the only authority.

### Output

Return structured policy sections containing:

- section number
- clause number
- clause text

The original meaning and binding requirements must be preserved.

---

## Skill: summarize_policy

### Purpose
Create a compliant summary from the structured policy sections returned by `retrieve_policy`.

### Input

Structured numbered policy sections.

### Process

1. Summarize every numbered clause.
2. Keep the original clause number with each summary item.
3. Preserve every obligation and condition.
4. Preserve all numerical values, dates, deadlines, limits, and thresholds.
5. Preserve all required approvers.
6. Preserve exceptions and "regardless of" conditions.
7. Do not weaken binding language.
8. Do not add external HR practices or assumptions.
9. If a clause cannot be safely summarized without losing meaning, quote it verbatim and flag it for review.
10. Perform a final completeness check against the source before returning the summary.

### Critical Multi-Condition Rule

When a clause contains multiple required conditions, ALL conditions must appear in the summary.

For example, Clause 5.2 requires:

- Department Head approval
- AND HR Director approval
- Manager approval alone is not sufficient

The summary must retain all three points.

### Critical Prohibition Rule

Negative requirements must remain negative.

For example, Clause 7.2 states that leave encashment during service is not permitted under any circumstances.

Do not rewrite this as a recommendation or general guidance.

### Output

Return a concise, structured policy summary with:

- clause number
- summary of the requirement
- all necessary conditions and exceptions

Every source clause must be represented.
