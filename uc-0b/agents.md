# UC-0B Policy Summary Agents

## Agent 1 — Policy Reader Agent
Reads the full HR policy document.

Responsibilities:
- Parse document sections
- Identify numbered clauses

## Agent 2 — Clause Preservation Agent
Ensures all mandatory clauses remain in the summary.

Responsibilities:
- Detect clauses like 2.3, 2.4, etc.
- Prevent clause omission

## Agent 3 — Policy Summarizer Agent
Produces a concise summary while preserving rules.

Rules:
- Do not weaken policy conditions
- Do not merge separate clauses