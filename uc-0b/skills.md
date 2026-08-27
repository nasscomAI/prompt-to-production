# skills.md — UC-0B Summary That Changes Meaning

## Skill: retrieve_policy
- **Input**: Path to policy file (e.g. `policy_hr_leave.txt`)
- **Process**: Load `.txt` policy file, parse numbered sections and clauses (e.g., Section 1, Section 2, Section 3, Section 4, Section 5, Section 6, Section 7, Section 8).
- **Output**: Structured mapping of policy sections and clause texts.

## Skill: summarize_policy
- **Input**: Structured policy document
- **Process**:
  1. Iterate through sections, ensuring all key numbered clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are systematically summarized.
  2. Enforce strict binding language (must, requires, will, not permitted).
  3. Explicitly verify multi-approver requirements (e.g., Clause 5.2 requires BOTH Department Head and HR Director).
  4. Ensure zero additions/external assumptions.
- **Output**: Plain-text structured summary formatted with clause numbers and exact obligations.
