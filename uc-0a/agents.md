# UC-0A Agents

This document defines the agents responsible for executing UC-0A — Complaint Classifier.

---

## Complaint Classifier Agent

Responsible for category assignment, priority detection, reason generation, and ambiguity handling.

**Key Constraints**
- Never invent categories
- Never downgrade priority when severity keywords exist
- Always provide a one-sentence reason
- Flag ambiguous cases conservatively

---

## Batch Processing Agent

Handles CSV ingestion and output generation.

Responsibilities:
- Read input CSV
- Invoke Complaint Classifier Agent per row
- Write validated output CSV

---

## Reviewer Agent

Validates rule compliance without reclassifying content.
