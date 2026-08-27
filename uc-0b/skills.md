skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured, numbered sections for precise analysis.
    input: File path (String) to the .txt policy document.
    output: Structured representation (List/Dictionary) of the policy, mapped by clause numbers.
    error_handling: Reports if the file is missing, empty, or if numbering patterns are inconsistent.

  - name: summarize_policy
    description: Generates a condensed summary of the policy sections while strictly preserving all obligations, conditions, and original clause numbers.
    input: Structured policy sections (from retrieve_policy).
    output: A summary document where every original clause is accounted for with its core obligations intact.
    error_handling: Identifies clauses with complex multi-part conditions that cannot be simplified without meaning loss and flags them for verbatim retention.
