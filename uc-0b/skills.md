# skills.md — UC-0B Policy Document Summarizer

## Skill 1: `retrieve_policy`
**Purpose**: Load a policy document (.txt) and return its content as structured numbered sections.

**Input**: Path to the policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).

**Output**: A dictionary where keys are clause numbers (e.g., `2.3`) and values are the corresponding text.

**Rules**:
- Preserve the exact text of each clause.
- Handle section headers and numbering (e.g., `2.3`, `3.2`).

---

## Skill 2: `summarize_policy`
**Purpose**: Generate a compliant summary of the policy document.

**Input**: Structured policy content (output of `retrieve_policy`).

**Output**: A text file summarizing all clauses while preserving obligations and conditions.

**Rules**:
- Include every numbered clause from the source document.
- Preserve all conditions and obligations verbatim.
- Flag clauses that cannot be summarized without meaning loss.