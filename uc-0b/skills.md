skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and extracts structured numbered sections by clause id.
    input: input_path (string path to policy text file).
    output: Dictionary with raw_text and sections map {clause_id: clause_text}.
    error_handling: Raises error if file is missing/unreadable or numbered clauses cannot be parsed.

  - name: summarize_policy
    description: Produces a compliant summary with clause references while preserving obligations and conditions.
    input: sections map from retrieve_policy and a required clause id list.
    output: Summary text with one line per required clause in deterministic clause order.
    error_handling: Raises refusal-style error when required clauses are missing or ambiguous; avoids speculative content.
