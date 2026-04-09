
skills:
  - name: retrieve_policy
    description: Loads a .txt policy file, returning its content as structured numbered sections.
    input:
      - name: input_path
        type: string
        format: File path (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output:
      type: Dict[str, str]
      format: A dictionary where keys are clause numbers (e.g., "2.3") and values are the full text of that clause.
    error_handling: Raises FileNotFoundError if the path is invalid. Returns an empty dictionary if the file is empty or no clauses are found.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, adhering to enforcement rules.
    input:
      - name: policy_sections
        type: Dict[str, str]
        format: Dictionary of clause numbers to their full text, as produced by 'retrieve_policy'.
      - name: clause_inventory
        type: List[Dict[str, str]]
        format: A list of dictionaries, each containing 'Clause', 'Core obligation', and 'Binding verb' for ground truth clauses.
    output:
      type: string
      format: A markdown-formatted string representing the policy summary, including clause numbers and flags.
    error_handling: Adds flags within the summary itself (e.g., "(FLAG: Verbatim Quote - No specific summary logic)", "(FLAG: Meaning Loss - Conditions)") if a clause cannot be clearly summarized or if conditions might be lost.

