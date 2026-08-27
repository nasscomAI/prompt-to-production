skills:
  - name: retrieve_policy
    description: "Reads the raw .txt policy file and extracts its content, structuring it into numbered sections for analysis."
    input: "file_path (string) - Path to the policy text document."
    output: "structured_sections (list) - An inventory of policy sections broken down by their numbered clauses."
    error_handling: "If the file is not found or fails to load, explicitly return an error stating the policy file could not be accessed rather than hallucinating text."

  - name: summarize_policy
    description: "Processes structured policy sections to generate a concise summary that strictly preserves binding verbs and multi-condition obligations."
    input: "structured_sections (list) - The mapped collection of clauses provided by the retrieve_policy skill."
    output: "summary (string) - A compliant summary text mapped by clause references, including verbatim quotations for ambiguous sections."
    error_handling: "If a specific section's meaning cannot be retained without meaning loss during summarization, quote the policy verbatim and append a [VERBATIM FLAG]."
