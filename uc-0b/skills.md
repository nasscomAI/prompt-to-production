skills:
  - name: retrieve_policy
    description: Load the text of a policy document and parse it into a structured dictionary mapping clause numbers to their text.
    input:
      type: string
      format: Path to the policy text file.
    output:
      type: dict
      format: Mapping of clause numbers (e.g., '2.3') to clause description strings.
    error_handling: >
      If the file is not found, raise FileNotFoundError.
      If the text format is unexpected, parse as much as possible and return the parsed dict.

  - name: summarize_policy
    description: Generate a structured summary of the policy document by extracting the targeted clauses verbatim, ensuring absolute meaning preservation.
    input:
      type: dict
      format: Structured dictionary mapping clause numbers to text strings.
    output:
      type: string
      format: Multiline summary string listing every target clause verbatim with an obligation flag.
    error_handling: >
      If a required target clause is missing from the input dictionary, record an error placeholder for that clause in the output summary.
