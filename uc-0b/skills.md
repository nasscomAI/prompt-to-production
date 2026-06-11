skills:
  - name: retrieve_policy
    description: "Loads the .txt policy file and returns the content as structured numbered sections."
    input:
      type: string
      format: "File path to the .txt policy document"
    output:
      type: array
      format: "List of objects representing numbered sections/clauses and their text"
    error_handling: "If the file cannot be read, return an error. If the text does not contain numbered sections, raise a parsing error instead of guessing."

  - name: summarize_policy
    description: "Takes structured sections and produces a compliant summary with clause references."
    input:
      type: array
      format: "List of structured numbered sections"
    output:
      type: string
      format: "Compliant summary text with explicit references to clause numbers"
    error_handling: "If a clause cannot be confidently summarized without losing conditions (such as multiple approvers or specific deadlines), output the exact verbatim text for that clause and append a '[VERBATIM FLAG]' warning."
