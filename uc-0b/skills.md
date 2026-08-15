# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured numbered sections for clause-level processing.
    input: Path to a policy .txt file (expected: `../data/policy-documents/policy_hr_leave.txt`).
    output: Structured text where each numbered clause (e.g. 2.3, 5.2) is isolated as its own section with section headings intact.
    error_handling: If the file is missing, unreadable, or not the expected leave-policy document, returns an error and refuses to proceed rather than guessing.

  - name: summarize_policy
    description: Takes the structured numbered sections and produces a compliant plain-English summary with clause references.
    input: Structured numbered sections from `retrieve_policy`, plus the clause inventory from README.md as a cross-check.
    output: A single summary .txt (written to `uc-0b/summary_hr_leave.txt`) with clause references, representing every numbered clause, preserving all multi-condition obligations verbatim, and adding no information absent from the source.
    error_handling: If a clause cannot be summarised without meaning loss, quotes it verbatim and flags it with its clause number; refuses if the clause inventory cannot be established.
