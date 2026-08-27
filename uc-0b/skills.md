# skills.md

skills:
  - name: retrieve_policy
    description: Loads a text policy file and structures its numbered sections.
    input: input_path (str) to the policy text file.
    output: dict mapping clause numbers (str) to their exact text content (str).
    error_handling: Raises FileNotFoundError if the file doesn't exist, and outputs empty dict if the file contains no parseable sections.

  - name: summarize_policy
    description: Generates a faithful summary of target clauses without omitting any conditions or scope.
    input: clauses_dict (dict) mapping clause numbers to text.
    output: summary_text (str) containing formatted bullet points of each summarized clause.
    error_handling: Verbatim quotes the clause in the output if it cannot be safely summarized without meaning loss.
