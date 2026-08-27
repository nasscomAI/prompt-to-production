# UC-X Final Civic Tech Assistant — Agent Definition

## Role

A **Civic AI Assistant** that combines complaint classification, policy lookup, and budget validation into a single conversational interface. The user types a question (e.g., "Is my ward budget overspending on roads?"), and the system analyzes the available data and responds with structured reasoning. No external APIs — uses only the data files in the repository.

## Intent

A correct output is:

- **Structured response**: JSON or formatted text with: `intent`, `answer`, `reasoning`, `data_sources`
- **Intent**: Detected user intent (budget, policy, complaint, or combined)
- **Answer**: Direct answer to the question
- **Reasoning**: Step-by-step explanation of how the answer was derived
- **Data sources**: Which files were used (e.g., ward_budget.csv, policy_hr_leave.txt)

## Context

The agent may use:

- `data/budget/ward_budget.csv` for budget queries
- `data/policy-documents/*.txt` for policy queries
- `data/city-test-files/*.csv` for complaint queries
- Inline implementations of classifier, policy extractor, and budget validator

Exclusions:

- No external LLM or API calls
- No user authentication or personal data storage

## Task Flow

1. **Parse** — Detect user intent from question (budget, policy, complaint)
2. **Route** — Invoke appropriate analyzer(s)
3. **Analyze** — Run classification, policy lookup, or budget validation
4. **Synthesise** — Combine results into a coherent answer
5. **Respond** — Output structured reasoning and answer

## Reasoning Approach

- **Intent detection**: Keyword matching — "ward", "budget", "overspend", "roads" → budget
- **Budget**: Load CSV, filter by ward/category, compare actual vs budget, compute overspend %
- **Policy**: Load policy files, extract relevant sections by keyword
- **Complaint**: Load complaint CSVs, run classifier, aggregate by category

## Enforcement Rules

- Every response must include reasoning
- Must cite data source (file name)
- If data is missing, say "No data available for X" rather than guessing
- Handle unknown intents with "I can help with: budget questions, policy lookup, complaint summaries"
