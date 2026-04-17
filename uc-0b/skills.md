# UC-0B — Policy Integrity Skills

## Skill 1: Formal Clause Extraction
- **Input**: Raw text from `policy_hr_leave.txt`.
- **Logic**: Use regex or LLM grounding to split the document into its original structured sections (e.g., Definitions, 1.1, 1.2, etc.).
- **Constraint**: Do not omit any section, even if it looks like metadata.

## Skill 2: Multi-Condition Obligation Mapping
- **Input**: A single clause text.
- **Logic**: Identify all actors, conditions, and permissions.
    - *Example*: "Leave requires (1) 48h notice AND (2) supervisor signature."
- **Output**: A structured list of requirements that **must** be present in the final summary.

## Skill 3: High-Fidelity Summarization
- **Input**: Clause mappings.
- **Logic**: Generate professional, concise descriptions.
- **Strict Rule**: If a clause cannot be summarized without dropping a condition, use the **[VERBATIM]** skill to quote it exactly.

## Skill 4: Integrity Verification
- **Input**: Final Summary vs Original Inventory.
- **Logic**: Self-audit. If Clause X is in the inventory but missing from the summary, regenerate. If any condition was "simplified" (lost), restore it.
