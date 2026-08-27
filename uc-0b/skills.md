skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and extracts its contents into structured, numbered sections as a precise source of truth.
    input: File path string to a .txt policy document (e.g., policy_hr_leave.txt).
    output: Structured text containing the exact, sequentially numbered clauses.
    error_handling: Refuse to proceed and throw an error if the file cannot be accessed or is improperly formatted.

  - name: summarize_policy
    description: Takes structured policy sections and produces a 100% compliant, exhaustive summary that preserves all original numbered clauses and their multi-condition obligations.
    input: Structured policy sections extracted by the retrieve_policy skill.
    output: A comprehensive summary text document ensuring no clause or multi-condition obligation is dropped, softened, or scope-bled.
    error_handling: If a clause condition cannot be fully captured without meaning loss, quote it verbatim and flag it in the output. If input sections are empty or corrupt, refuse to generate a summary.
