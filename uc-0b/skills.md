# skills.md

skills:
  - name: retrieve_policy
    description: Loads a raw text policy document from the filesystem and parses its content into structured, numbered sections mapping clause identifiers to their raw text.
    input: A string representing the absolute or relative path to the input policy `.txt` file.
    output: A dictionary mapping clause numbers (e.g., "2.3", "5.2") to their respective raw text blocks.
    error_handling: If the input file path is invalid, missing, or empty, raises a FileNotFoundError or ValueError with a descriptive message rather than failing silently.

  - name: summarize_policy
    description: Processes structured policy sections, verifies the presence of all ten key target clauses, and generates a precise summary that strictly preserves all binding verbs, approvals, and multi-condition obligations.
    input: A dictionary of structured policy sections (keys are clause numbers, values are raw text) and a string representing the target output file path.
    output: Writes the verified summary containing all ten key clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2) to the target file path and returns the text content of the summary.
    error_handling: If a target clause is missing from the input, or if it cannot be summarized without softening or losing its precise multi-condition requirements (e.g., dropping an approver from Clause 5.2), quotes the clause verbatim, prefixes/flags it as unsummarizable, and continues.
