# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause numbers preserved.
    input: File path to a .txt policy document (e.g. policy_hr_leave.txt).
    output: A list of sections, each containing a section title and a list of numbered clauses with their full text and binding verbs identified.
    error_handling: If the file does not exist or cannot be parsed into sections, returns an error message with the file path and reason. Never returns partial data without flagging what is missing.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving every clause reference, all conditions, and all binding verbs at original strength.
    input: Structured sections from retrieve_policy — a list of sections each containing numbered clauses.
    output: A text summary organised by section, with every clause referenced by number, all multi-condition obligations fully preserved, and no added information.
    error_handling: If a clause cannot be summarised without meaning loss, includes it verbatim with a [VERBATIM] flag. If a multi-condition clause is detected, explicitly lists all conditions to prevent silent dropping.
