# skills.md

skills:
  - name: retrieve_policy
    description: Reads the raw .txt policy file and extracts its contents as structured, numbered section data.
    input: An absolute or relative file path pointing to a policy text file.
    output: A structured string or dict representation containing all the numbered clauses explicitly captured.
    error_handling: Refuses to proceed and raises a file-not-found error or standard output log if the file cannot be read.

  - name: summarize_policy
    description: Takes the structured policy sections and outputs them strictly preserving multi-condition requirements and clause numbers without adding unverified context.
    input: The structured data returned from retrieve_policy.
    output: A single formatted string containing the compliant summary text with all relevant numbered clause references accurately mapped.
    error_handling: Halts and outputs an error string if requested to summarize text in a way that risks omitting obligations.
