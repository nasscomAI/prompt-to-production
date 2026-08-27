skills:
  - name: retrieve_policy
    description: "Loads the input text policy file and extracts its contents as strictly structured, numbered sections."
    input: "File path string to the source .txt policy document."
    output: "A structured format containing the intact numbered clauses and their exact textual content."
    error_handling: "If the file cannot be found or the content lacks clearly numbered clauses, the skill immediately throws an error and aborts execution to prevent any implicit omissions before summarization begins."
  - name: summarize_policy
    description: "Transforms structured policy sections into a compliant, referenced summary while strictly preserving all original conditions and obligations."
    input: "The structured, numbered sections extracted from the source policy document."
    output: "A fully unified compliant summary text explicitly referencing every numbered clause."
    error_handling: "To prevent clause omission, validation fails if any numbered clause is missing. To prevent condition drops, any obligation that cannot be safely summarized is quoted verbatim and flagged. To prevent scope bleed, if generated extrapolations or unprovided contexts are detected, the summary is rejected and regenerated."
