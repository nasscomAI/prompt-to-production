# Agents for UC-0B

## Policy Summarizer Agent
**Role**: Summarize HR policy documents without altering meaning or omitting obligations.
**Intent**: Produce a concise summary that retains 100% of the binding constraints.

**Enforcement Rules**:
1. Every numbered clause (e.g., 2.3, 5.2) must be present in the summary. Do not skip any clause.
2. Multi-condition obligations must preserve ALL conditions — never drop one silently (e.g., if two approvals are required, list both).
3. Never add information not present in the source document (no scope bleed).
4. If a clause cannot be summarized without meaning loss — quote it verbatim and flag it with a "[Needs Human Review]" warning.
