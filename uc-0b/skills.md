# skills.md

skills:
  - name: summarize_policy
    description: Summarizes an HR leave policy document into a concise summary that includes all numbered clauses with their core obligations and binding verbs preserved, ensuring no omissions, softenings, or additions.
    input: Path to the input policy document file (string, .txt format).
    output: Writes the summary text to the specified output file path (string).
    error_handling: Raises exceptions for file I/O errors; ensures summary is generated only from valid input text.
