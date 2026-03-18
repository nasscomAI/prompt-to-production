# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: extract_policy_rules
    description: Extracts structured rules from a policy document without adding or changing meaning
    input: policy document text
    output: list of rules with conditions and constraints
    rules:
      - Must not paraphrase away conditions
      - Must preserve numbers, limits, and thresholds exactly
      - Must not infer missing information
      - Each rule must remain grounded in source text

  - name: summarize_policy
    description: Generates a concise but accurate summary of a policy document
    input: policy document text
    output: structured summary
    rules:
      - Do not drop conditions or exceptions
      - Do not generalize specific rules
      - Keep numerical values exact
      - Avoid adding external knowledge