# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.
skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: file path (str) to a .txt policy document.
    output: A list/dict of sections, each keyed by clause number, containing the clause's raw text.
    error_handling: If the file is missing or a clause number can't be parsed, log a warning and return whatever sections were successfully parsed rather than crashing.

  - name: summarize_policy
    description: Takes structured clause sections and produces a compliant summary that references every clause number and preserves all conditions.
    input: Structured sections (from retrieve_policy).
    output: A plain text summary, one line/paragraph per clause, each prefixed with its clause number.
    error_handling: If a clause's meaning can't be safely condensed without dropping a condition, output the clause verbatim with a "[VERBATIM — FLAGGED]" marker instead of a paraphrase.
