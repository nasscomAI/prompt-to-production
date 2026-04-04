# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads and parses a .txt policy file, returning content as structured numbered sections.
    input: File path to policy document (string). Example: `../data/policy-documents/policy_hr_leave.txt`
    output: Dictionary/object with numbered sections (e.g., "2.3", "2.4", "5.2") as keys and full clause text as values.
    error_handling: Return descriptive error if file not found, unreadable, or cannot be parsed as structured numbered sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-complete summary with explicit references to source clause numbers.
    input: Structured policy sections (output from retrieve_policy) + clause inventory mapping (list of required clause IDs).
    output: Summary text preserving all clauses and conditions with clause number references. Must include all required clauses from inventory.
    error_handling: Refuse to output if any required clauses are missing from summary. Flag and quote any clauses at risk of meaning loss or condition drop.
