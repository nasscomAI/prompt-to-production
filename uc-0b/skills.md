# UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses its content into a structured format organized by numbered clauses.
    input: Absolute path to the policy .txt file.
    output: A structured object containing clause numbers as keys and their full text as values.
    error_handling: Return an error message or empty object if the file is missing, empty, or lacks numbered clauses.

  - name: summarize_policy
    description: Generates a compliant summary of the structured policy clauses, ensuring no conditions and clauses are dropped and all obligations remain binding.
    input: Structured policy data (clause numbers and text).
    output: A summarized policy document preserving all clause references and multi-condition rules.
    error_handling: If a clause's meaning is compromised by summarization, the skill must quote the original text verbatim and add a 'NEEDS_MANUAL_REVIEW' flag.

