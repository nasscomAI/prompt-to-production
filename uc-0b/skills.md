skills:
  - name: "retrieve_policy"
    description: "Reads the .txt policy file, parses the document line-by-line, and extracts the content as structured numbered sections."
    input:
      file_path: "string (path to the text document)"
    output:
      structured_sections: "list of dictionaries containing 'clause_number' and 'content'"
    error_handling: "If the input file is missing, raise FileNotFoundError. If the file is empty, return a specific error string."

  - name: "summarize_policy"
    description: "Processes structured sections to produce a compliant summary. Applies verbatim flagging to prevent meaning loss or condition dropping."
    input:
      structured_sections: "list of dictionaries (parsed policy data)"
    output:
      summary_text: "string (the final formatted summary with clause references)"
    error_handling: "If a clause contains complex multi-condition logic that cannot be safely abstracted, immediately apply Enforcement Rule 4 and quote it verbatim with a [VERBATIM FLAG]."