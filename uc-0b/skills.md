skills:
  - name: retrieve_policy
    description: "Reads a raw text-based policy document and parses it into a structured format keyed by clause numbers."
    input: "Path to input policy .txt file."
    input_format: File path (string)
    output: "A dictionary mapping each numbered clause (e.g., '2.3') to its full textual content."
    output_format: Dict { "X.Y": "text..." }
    error_handling: "Raises an error if the file is missing or lacks clear numbering prefixes (e.g., '1.1')."

  - name: summarize_policy
    description: "Generates a high-fidelity summary of structured policy clauses, ensuring all multi-condition rules and mandatory verbs are preserved."
    input: "Dictionary of structured policy clauses."
    input_format: Object/Dict
    output: "A formatted text string containing the clause-by-clause summary."
    output_format: String
    error_handling: "If a targeted clause like 5.2 or 7.2 is missing or if conditions are dropped, this skill must flag the summary for manual verification."
