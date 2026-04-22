
# Skills — UC‑0B Enforcement Skills

These skills are mandatory for preventing meaning drift in policy summarization workflows.

---

## Skill: retrieve_policy

### Description
Loads a policy document from a `.txt` file and returns it as structured, numbered sections.

### Inputs
- File path to policy `.txt` document

### Outputs
- Structured representation containing:
  - Clause numbers
  - Raw clause text

### Constraints
- Must preserve original wording
- Must not infer or rephrase content
- Section numbering must match source exactly

---

## Skill: summarize_policy

### Description
Generates a policy summary that **preserves all obligations, conditions, and legal force**.

### Inputs
- Structured policy sections from `retrieve_policy`

### Output Requirements
- Every clause must appear in the summary
- Binding verbs must be preserved
- Multi‑condition clauses must retain **all** conditions

### Special Handling
- If summarization causes loss of meaning:
  - Quote the clause verbatim
  - Flag it explicitly as high‑risk for summarization

---

## Enforcement Logic
The following checks are mandatory after summarization:

- Clause presence verification
- Condition completeness verification
- Language strength comparison (original vs summary)

Failure to meet any check results in **summary rejection**.

---

## Non‑Goals
The skills explicitly do **not**:
- Interpret intent
- Apply external norms
- Compare with other organizational policies
- Perform best‑practice generalizations

---

## Design Principle
**Summarization is compression, not interpretation.**
