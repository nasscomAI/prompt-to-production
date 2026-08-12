# UC-0B Policy Summarizer Skills

## Defined Skills

### 1. `retrieve_policy`
- **Description**: Reads policy text files, parses sections and numbered clauses into a structured representation.
- **Input**: Path to policy document file.
- **Output**: Dictionary of structured clause items (clause number, raw text, section title).

### 2. `summarize_policy`
- **Description**: Evaluates structured clause items against compliance rules, ensuring all binding conditions and dual-approvers are preserved.
- **Input**: Structured clause dictionary.
- **Output**: Verbatim/compliant text summary mapped clause by clause.
