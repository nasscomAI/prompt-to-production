skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as a list of structured, numbered sections for precise summarization.
    input: String path to the `.txt` policy document.
    output: List of dictionaries, each containing `clause_id` (string) and `verbatim_text` (string).
    error_handling: Refuse to process if the file is not a `.txt` format or if the file cannot be found.

  - name: summarize_policy
    description: Generate a condensed summary of structured policy sections while preserving all binding obligations and multi-condition rules.
    input: Structured policy sections (list of dicts) and the reference "Clause Inventory."
    output: A structured summary text file (e.g., `summary_hr_leave.txt`) that maps back to original clause numbers.
    error_handling: If a clause cannot be summarized without losing a condition, quote it verbatim and flag it.
