# skills.md — UC-0B Policy Summarization Skills

skills:
  - name: retrieve_policy
    description: "Extracts and cleans text from a policy document, splitting it into addressable numbered sections for individual analysis."
    input:
      type: string
      description: "Path to the policy text file."
    output:
      type: object
      description: "A dictionary mapping clause numbers (e.g. '2.3') to their full text content."
    error_handling:
      - scenario: "File not found"
        action: "Raise clear error specifying the missing path."
      - scenario: "Document has non-standard numbering"
        action: "Use fallback regex patterns to identify paragraph boundaries if explicit numbers are missing."

  - name: summarize_policy
    description: "Transforms structured policy sections into a concise summary while maintaining 100% fidelity to core obligations and approval conditions."
    input:
      type: object
      description: "Dictionary of identified mandatory clause sections."
    output:
      type: string
      description: "A structured text summary formatted point-by-point with clause references."
    error_handling:
      - scenario: "Clause contains complex 'AND/OR' conditions (e.g. 5.2)"
        action: "Expand the summary to explicitly name all required distinct approvers or conditions to prevent silent dropping."
      - scenario: "Mandatory clause is missing from input dictionary"
        action: "Note the missing clause in the summary and output a warning to the log."

  - name: validate_fidelity
    description: "Cross-checks the generated summary against the source text to ensure no scope bleed or condition softening occurred."
    input:
      type: object
      properties:
        source_text: { type: string }
        summary_text: { type: string }
    output:
      type: boolean
    error_handling:
      - scenario: "Detected words like 'generally', 'typically', or 'usually' not in source"
        action: "Flag as scope bleed and trigger a rewrite of the affected section."
