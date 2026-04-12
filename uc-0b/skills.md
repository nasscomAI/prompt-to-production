# skills.md

skills:
  - name: retrieve_policy
    description: Load and parse HR leave policy document into structured numbered sections.
    input: File path to policy .txt file (e.g., policy_hr_leave.txt).
    output: Dictionary with clause numbers as keys (e.g., '2.3', '5.2'). Each entry contains clause_text, binding_verb, obligations list, and dependency conditions if multi-part.
    error_handling: If file missing, raise FileNotFoundError. If clause structure malformed, preserve raw text and flag MALFORMED. If binding verb absent, flag UNCLEAR_OBLIGATION.

  - name: summarize_policy
    description: Produce policy summary preserving all clauses and multi-condition requirements with no scope bleed.
    input: Structured policy dictionary from retrieve_policy skill.
    output: Summary text with clause references preserved. Multi-condition clauses listed with ALL conditions. Scope bleed indicators removed. Flagged clauses marked [QUOTED] or [CONFLICT] if needed.
    error_handling: If clause has complex nested conditions, preserve verbatim. If binding verb missing, output flag UNCLEAR. If text >300 chars and cannot be simplified, quote verbatim and mark [QUOTED]."
