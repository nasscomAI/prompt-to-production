skills:
  - name: retrieve_policy
    description: Loads the raw text of a policy file and parses it into structured numbered sections.
    input:
      type: str
      format: Path to the .txt policy file.
    output:
      type: dict
      format: A dictionary mapping section/clause numbers (strings like '2.3') to their raw text content.
    error_handling:
      rules:
        - "If the file does not exist, raise FileNotFoundError."
        - "If the file is empty, return an empty dictionary."

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant, complete summary highlighting the core obligations with clause references.
    input:
      type: dict
      format: A dictionary mapping section/clause numbers to their raw text content.
    output:
      type: str
      format: The formatted summary string containing all target clauses, their binding verbs, and conditions.
    error_handling:
      rules:
        - "If any required target clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing from the input dictionary, raise a ValueError."
        - "If a clause is found but cannot be safely summarized without meaning loss, output it verbatim labeled with [VERBATIM]."
