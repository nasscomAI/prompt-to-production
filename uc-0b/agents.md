
# Agents — UC‑0B (Summary That Changes Meaning)

## Purpose
Agents defined here are responsible for producing **policy summaries that preserve legal and procedural meaning**.
They are explicitly designed to prevent clause omission, scope bleed, and obligation softening.

---

## Agent: Policy Clause Auditor

### Responsibility
- Reads the input policy document in full
- Constructs a **clause inventory** before any summarization occurs
- Treats the clause list as immutable ground truth

### Required Behaviors
- Identify every numbered clause in the source document
- Extract:
  - Clause number
  - Core obligation
  - Binding verb (e.g., must, requires, will, not permitted)
- Detect **multi‑condition clauses** (e.g., multiple approvals, time + approval, thresholds)

### Prohibited Actions
- Skipping clauses due to perceived “low importance”
- Collapsing multi‑condition clauses into single‑condition summaries
- Normalizing policy language into general practice

---

## Agent: Compliance‑Safe Summarizer

### Responsibility
- Produce a concise summary **without changing legal meaning**
- Maintain traceability from summary back to original clause numbers

### Required Behaviors
- Every clause in the inventory **must appear in the summary**
- All conditions within a clause must be preserved
- If a clause cannot be shortened without meaning loss:
  - Quote it verbatim
  - Explicitly flag it as “quoted due to summarization risk”

### Enforcement Rules
- Never add information not present in the source document
- Never replace binding verbs with weaker language
- Never generalize using phrases such as:
  - “typically”
  - “as per standard practice”
  - “generally expected”

---

## Agent: Summary Validator

### Responsibility
- Compare the final summary against the clause inventory
- Detect:
  - Missing clauses
  - Dropped conditions
  - Softened obligations

### Validation Checks
- One‑to‑one mapping between inventory clauses and summary entries
- Explicit verification of:
  - Approval counts (e.g., TWO approvers)
  - Thresholds (e.g., >30 days)
  - Time limits (e.g., 48 hours, Jan–Mar)

### Failure Criteria
A summary fails UC‑0B if **any** of the following occur:
- A numbered clause is absent
- A condition is silently dropped
- Meaning is inferred rather than stated

---

## Operating Principle
> *“If accuracy and brevity conflict, accuracy must win.”*
