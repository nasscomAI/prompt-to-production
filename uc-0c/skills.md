skills:
  - name: compute_growth
    description: Processes a chronological table filtered down to a targeted subset, evaluating sequential MoM or YTD trends into decoupled columns.
    input: Datastore row array accompanied by target string filter strings.
    output: List of schema-compliant dictionary entries with structured growth_percent, formula, status, and null_reason text strings.
    error_handling: Automatically generates status labels like PREVIOUS_PERIOD_NULL when context calculations are disrupted by empty cells.