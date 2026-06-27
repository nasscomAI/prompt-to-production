# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a plain text HR policy file and extracts its content as structured, numbered clauses and sections.
    input: type: string
format: File path to a .txt policy document (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: type: array
format: If the input file is missing, empty, or cannot be structured into clear numbered sections, the skill raises a FileNotFoundError or data formatting exception instead of silently skipping sections.

  - name: summarize_policy
    description: Takes structured policy sections and generates a highly accurate summary that preserves all mandatory conditions and clause references.
    input: type: array
format: A structured list of numbered clauses with their corresponding constraints and obligations.
    output: type: string
format: A compliant text summary explicitly containing every numbered clause and all accompanying conditions.
    error_handling: If any clause is omitted, multi-condition requirements are dropped, or scope bleed/extrapolations are introduced, the skill flags the execution as a failure, quotes the affected clauses verbatim, and prevents generation of a faulty summary.
