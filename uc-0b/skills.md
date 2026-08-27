skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to a .txt HR policy document.
    output: Structured text with numbered sections preserved as found in the source document.
    error_handling: If the file is missing, unreadable, or contains no numbered sections, raise an error and halt — do not attempt to infer or reconstruct content.

  - name: summarize_policy
    description: Takes structured numbered policy sections and produces a compliant clause-by-clause summary with clause references.
    input: Structured numbered sections (string) as returned by retrieve_policy.
    output: A clause-referenced summary where every numbered clause is present, all conditions are preserved, and no external information is added.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it explicitly rather than paraphrasing.
