skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content parsed as structured numbered sections.
    input: File path to the .txt policy document (specifically ../data/policy-documents/policy_hr_leave.txt).
    output: A structured object or array containing numbered sections and their text.
    error_handling: If the file is missing or unreadable, return an error stating 'Policy file not found or inaccessible.' If parsing fails, return 'Document structure not recognized.'

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured object/array of numbered policy sections.
    output: A text summary saved to the output file (specifically uc-0b/summary_hr_leave.txt) containing all numbered clauses and their exact obligations.
    error_handling: If any clause cannot be summarized without loss of meaning, quote it verbatim and flag it in the summary. If inputs are missing, return an error requesting the structured clauses.
