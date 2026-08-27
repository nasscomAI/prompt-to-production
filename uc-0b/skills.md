skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into a structured collection of numbered sections for precise tracking.
    input: File path (string) to the .txt policy document.
    output: List of structured objects containing clause numbers and their raw text content.
    error_handling: Reports an error if specifically numbered clauses (e.g., 2.3, 5.2) are missing from the source to prevent unintentional clause omission.

  - name: summarize_policy
    description: Condenses structured policy sections into a compliant summary while strictly preserving all multi-condition obligations and binding verbs.
    input: List of structured objects containing clause numbers and content.
    output: Compliance-compliant summary text (string) with clause references.
    error_handling: Flags sections for verbatim quotation if meaning loss is detected and filters out any external "scope bleed" language not present in the source.
