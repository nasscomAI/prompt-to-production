skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections for analysis.
    input: File path (string) to the HR policy .txt file.
    output: A structured object mapping specific clause numbers (e.g., 2.3, 5.2) to their raw text content.
    error_handling: Throws an error if the file path is invalid, inaccessible, or if the document structure is unparseable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that enforces clause presence and multi-condition preservation.
    input: Structured policy content (object) and a reference inventory of mandatory clause numbers.
    output: A summary document where every mandatory clause is either summarized (preserving all conditions) or quoted verbatim if a lossless summary is impossible.
    error_handling: Returns a validation failure if any mandatory clause from the inventory is missing in the output summary.
