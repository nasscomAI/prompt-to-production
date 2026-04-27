
skills:
  - name: extract_rules
    description: >
      Extracts enforceable rules from policy text as structured data.
    input: Raw policy text
    output: List of rule objects (section, obligation, conditions)
    error_handling: Refuse if rules cannot be unambiguously extracted

  - name: summarize_rules
    description: >
      Condenses extracted rules into concise summary statements
      without changing meaning.
    input: Structured rule list
    output: Human-readable concise summary
    error_handling: Emit verbatim rule if condensation risks loss

  - name: validate_summary
    description: >
      Ensures all rules from the source appear in the summary.
    input: Source rules and generated summary
    output: Pass/fail with missing-rule list
    error_handling: Fail hard on any missing rule
