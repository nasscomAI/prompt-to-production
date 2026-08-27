# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured, numbered sections.
    input:
      type: object
      format: |
        {
          "input_path": "../data/policy-documents/policy_hr_leave.txt"
        }
    output:
      type: object
      format: |
        {
          "sections": [
            {
              "clause": "2.3",
              "text": "14-day advance notice required"
            },
            ...other clauses...
          ]
        }
    error_handling: |
      If the file is missing or unreadable, raise an error and halt. If the file cannot be parsed into numbered sections, flag the error and return as much structure as possible, marking ambiguous or missing clauses for review.
  - name: summarize_policy
    description: Take structured policy sections and produce a summary that references every clause, preserving all obligations and conditions.
    input:
      type: object
      format: |
        {
          "sections": [
            {
              "clause": "2.3",
              "text": "14-day advance notice required"
            },
            ...other clauses...
          ]
        }
    output:
      type: object
      format: |
        {
          "summary": "string",
          "flags": [
            {
              "clause": "5.2",
              "reason": "verbatim quoted due to summarization risk"
            }
          ]
        }
    error_handling: |
      If any clause cannot be summarized without meaning loss, quote it verbatim and add a flag. If a clause is missing, flag the omission. If input is malformed or ambiguous, halt and return an error with details. Never add information not present in the source.
