skills:
  - name: retrieve_policy
    description: Reads the HR leave policy text file and returns the numbered policy sections in a structured form.
    input: File path to a .txt policy document.
    output: Ordered dictionary or list of numbered clauses with their original text blocks.
    error_handling: If the file is missing, unreadable, or empty, raise a clear file error instead of guessing the content.

  - name: summarize_policy
    description: Converts the structured policy sections into a compliance-safe summary that keeps every clause and condition intact.
    input: Structured numbered sections plus the README clause inventory.
    output: Plain-text summary that preserves clause numbers and all required conditions, with verbatim quotes when needed.
    error_handling: If a required clause is missing, stop and flag the omission rather than creating a weaker paraphrase.
