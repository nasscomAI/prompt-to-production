skills:
  - name: retrieve_policy
    description: >
      Loads a raw text policy document from the filesystem and parses it into a structured format, explicitly identifying major headings and individual numbered clauses to prevent conflation or cross-contamination  during downstream processing.
    input:
      type: file path
      format: String pointing to the location of the raw .txt document (e.g., '../data/policy-documents/policy_hr_leave.txt')
    output:
      type: dictionary
      format: >
        {
          "sections": [
            {
              "heading": "string",
              "clauses": {
                "clause_number (e.g. '2.3')": "full text of the clause"
              }
            }
          ]
        }
    error_handling: >
      If the text file is improperly formatted, missing numbered clauses, or empty, it will halt processing 
      and log a fatal error rather than returning corrupt un-indexed strings that might cause downstream clause omissions.

  - name: summarize_policy
    description: >
      Iterates over the structured dictionary of policy clauses and produces a compliant summary. It utilizes exact regex-based or algorithmic mappings to guarantee that all key clauses (including multi-condition binding arrays) are retained and structured securely into the final report without scope bleed.
    input:
      type: dictionary
      format: Structured dictionary output provided directly by `retrieve_policy` containing mapped clauses.
    output:
      type: string
      format: A complete, fully formatted policy summary text containing all enforced clauses perfectly preserved.
    error_handling: >
      If a target clause required by the enforcement matrix is completely absent from the retrieved dictionary, the summarization function will explicitly insert a "[WARNING: CLAUSE OMITTED IN SOURCE]" placeholder rather than silently dropping the requirement and failing validation.
