skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: Filepath to the policy document (string).
    output: Structured representation of the policy document with distinct numbered sections, ensuring every clause is identified and separated.
    technical_details: >
      Must implement robust parsing (e.g., strict regex or line-by-line tokenization) to identify specific clause numbers (like 2.3, 2.4, 3.2) and extract their corresponding text precisely without merging distinct clauses or dropping edge cases.
    error_handling: Return an explicit error if the file cannot be found, read, or parsed into distinct numbered sections.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections of a policy.
    output: A summary text containing all clauses with their obligations strictly preserved, including all multi-condition requirements and binding verbs.
    business_rules: >
      - Must strictly map core obligations and preserve binding verbs (e.g., 'must', 'will', 'requires', 'are forfeited').
      - Validate that multi-condition clauses (like dual approvals or precise timeframes) are fully preserved and no condition drops occur.
      - Perform a validation pass on the output to ensure no hallucinated phrases (e.g., "standard practice") or scope bleed are injected.
    error_handling: Quote verbatim and flag any clause that cannot be summarized without altering its meaning.
