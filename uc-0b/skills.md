skills:
  - name: retrieve_policy
    description: Load a policy text file and parse its content into structured numbered sections.
    input: Path to the policy text file.
    output: A collection of structured sections, each with a clause identifier and the raw text content.
    error_handling: Raise an error if the policy file cannot be read, contains no recognizable numbered clauses, or is malformed.

  - name: summarize_policy
    description: Take structured policy sections and generate a precise summary where each clause is summarized or quoted verbatim according to strict enforcement rules.
    input: Structured policy sections.
    output: A formatted text summary with explicit clause references, preserving all obligations and conditions.
    error_handling: If any of the required clauses (e.g., 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing, flag the failure and abort or request regeneration.
