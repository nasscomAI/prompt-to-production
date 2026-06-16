skills:
  - name: retrieve_policy
    description: Optimized stream parsing of policy texts into isolated O(1) query-ready dictionaries.
    input: Path to the policy text file (string).
    output: List of dictionaries containing keys 'section' and 'content'.
    error_handling: System raises clean FileNotFoundError if the path target is unreachable.

  - name: summarize_policy
    description: Aggregates structured dictionary indexes into a complete line-by-line breakdown document.
    input: List of structured policy sections (list of dicts).
    output: A formatted, line-for-line output string.