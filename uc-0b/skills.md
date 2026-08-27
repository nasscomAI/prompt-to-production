# UC-0B Skills

## retrieve_policy

**Input:** Path to a .txt policy file

**Output:** Structured list of sections, each with heading and content

**Logic:**
1. Read the file content.
2. Split into sections based on separator lines (═══).
3. Return each section with its heading and full content preserved.

---

## summarize_policy

**Input:** Structured sections from retrieve_policy

**Output:** Compliant summary text with all clause references

**Logic:**
1. Extract document metadata (title, reference, version).
2. Parse every numbered clause (e.g., 2.3, 5.2) with full text.
3. Include multi-line continuation text for wrapped clauses.
4. Output each clause with its number in square brackets.
5. Append compliance note confirming no information was added.

**Enforcement:**
- Every numbered clause must be present in output.
- Multi-condition obligations preserve ALL conditions.
- Never add information not in the source document.
- Binding verbs (must, will, requires) are never softened.
