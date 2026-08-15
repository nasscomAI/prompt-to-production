skills:

  retrieve_policy:
    description: >
      Loads the supplied .txt HR leave policy and returns its contents
      as structured numbered sections while preserving clause numbers
      and the original wording.

    input:
      - policy_file

    output:
      - numbered_policy_sections

    rules:
      - Preserve every numbered clause.
      - Do not remove conditions, approvers, deadlines, limits, or exceptions.
      - Do not add information that is not present in the source.

  summarize_policy:
    description: >
      Takes structured policy sections and produces a compliant summary
      containing all required clause references and preserving every
      condition that affects the meaning of the policy.

    input:
      - numbered_policy_sections

    output:
      - clause_referenced_summary

    rules:
      - Include clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
      - Preserve all multi-condition requirements.
      - Preserve binding verbs and their meaning.
      - Do not introduce outside information.
      - Flag any clause that cannot be safely summarized without meaning loss.
