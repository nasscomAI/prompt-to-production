# UC-0B Agents

## Agent: Policy Summarizer

### Goal
Summarize HR leave policy without losing meaning or conditions.

### Enforcement Rules
1. Every numbered clause must be included in the summary
2. Multi-condition clauses must preserve ALL conditions
3. No new information should be added
4. If meaning loss occurs, quote clause verbatim

### Failure Modes Prevented
- Clause omission
- Scope bleed
- Obligation softening