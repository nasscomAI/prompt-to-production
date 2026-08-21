# UC-X Ask-My-Documents Agents

## Agent 1 — Query Understanding Agent
Interprets user question.

Responsibilities:
- Detect intent
- Identify relevant policy domain

## Agent 2 — Document Retrieval Agent
Selects the correct policy document.

Documents:
- HR Leave Policy
- IT Acceptable Use Policy
- Finance Reimbursement Policy

## Agent 3 — Policy Answer Agent
Generate answer using only one document.

Rules:
- Do not mix documents
- Cite relevant section

## Agent 4 — Refusal Agent
Handles unsupported questions.

Action:
Return standard refusal template when answer not found.