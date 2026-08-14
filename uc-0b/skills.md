# skills.md — UC-0B Skills

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses it into structured numbered sections and clauses.
    input: File path (string) to the .txt policy document.
    output: A dictionary mapping section numbers and clause numbers to raw text and headings.
    error_handling: Raises FileNotFoundError with clear message if file is missing; handles UTF-8 encoding safely.

  - name: summarize_policy
    description: Generates a lossless, structured policy summary enforcing all multi-condition rules and exact clause references.
    input: Structured policy sections (dict) or source text (string).
    output: A structured text summary preserving every binding clause, dual approvals, notice periods, and forfeiture rules.
    error_handling: Never omits required conditions; quotes ambiguous or complex multi-approver clauses verbatim.
