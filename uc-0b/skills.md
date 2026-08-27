# Skills for HR Policy Summarizer

This file defines the specific skills required by the HR Policy Summarizer agent to process the HR leave policy document.

## 1. retrieve_policy

**Description:** Loads the `.txt` policy file and returns the content as structured numbered sections.

**Inputs:**
- `file_path` (string): The path to the HR leave policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).

**Outputs:**
- `structured_sections` (list of objects): A parsed representation of the document where each numbered clause is cleanly separated and identifiable (e.g., `{"clause": "2.3", "text": "..."}`).

**Behavior:**
- Reads the raw text file from the given path.
- Parses the document to identify numbered clauses (e.g., "2.3", "5.2").
- Extracts the exact text associated with each clause verbatim.
- Returns the structured format to guarantee that the summarization step has an exhaustive inventory of all clauses.

---

## 2. summarize_policy

**Description:** Takes the structured sections and produces a compliant summary with clause references, adhering strictly to the agent's enforcement rules.

**Inputs:**
- `structured_sections` (list of objects): The parsed document outputted by `retrieve_policy`.

**Outputs:**
- `summary` (string): The final summarized HR leave policy document.

**Behavior:**
- Iterates through every single numbered clause provided in the structured input, ensuring none are omitted.
- Condenses the text while preserving all core obligations and binding verbs (e.g., "must", "requires", "will", "are forfeited").
- **Multi-Condition Preservation:** When encountering multi-condition obligations (e.g., requiring approval from Department Head AND HR Director), it explicitly includes ALL conditions. It never silently drops a required condition.
- **Scope Bleed Prevention:** Strictly avoids adding external information, assumptions, or "standard practices" that are not explicitly stated in the source text.
- **Meaning Loss Prevention:** If a clause's meaning cannot be safely condensed without risking obligation softening or meaning loss, it quotes the original clause verbatim and adds a flag to it in the summary.
- Formats the final output to include clear references to the original clause numbers.
