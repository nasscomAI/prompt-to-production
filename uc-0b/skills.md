# skills.md — UC-0B Policy Summary

skills:
  - name: retrieve_policy
    description: Loads policy text file and returns content as structured numbered sections with clause identifiers preserved.
    input: |
      - file_path (string) — path to .txt policy file (e.g., policy_hr_leave.txt)
    output: |
      Dictionary with structure:
      {
        "document_info": {
          "title": string,
          "reference": string,
          "version": string,
          "effective_date": string
        },
        "sections": [
          {
            "section_number": string (e.g., "2"),
            "section_title": string (e.g., "ANNUAL LEAVE"),
            "clauses": [
              {
                "clause_number": string (e.g., "2.3"),
                "clause_text": string (exact text from document),
                "binding_verbs": list of strings (e.g., ["must", "requires"])
              }
            ]
          }
        ],
        "total_clauses": int
      }
    error_handling: |
      - If file does not exist → raise FileNotFoundError with clear message
      - If file is empty → raise ValueError "Policy document is empty"
      - If no numbered clauses found → raise ValueError "Document does not contain numbered clauses"
      - If clause numbering is inconsistent → log warning but continue processing

  - name: summarize_policy
    description: Takes structured policy sections and produces compliant summary preserving all numbered clauses, multi-condition obligations, and binding verbs without adding external information.
    input: |
      - policy_data (dict) — output from retrieve_policy containing structured sections and clauses
      - output_path (string) — path where summary should be written
    output: |
      Text file written to output_path containing:
      - Document header (title, reference, version)
      - Summary organized by section
      - Every numbered clause present with citation (e.g., "[Clause 2.3]")
      - All multi-condition obligations preserved in full
      - No information added that is not in source document
      - Verification footer listing total clauses summarized
    error_handling: |
      - If any required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing from input → raise ValueError listing missing clauses
      - If multi-condition obligation detected (e.g., "A AND B") → verify both conditions are in summary, flag if dropped
      - If binding verb changed (must→should, requires→recommends) → reject summary and flag the violation
      - If scope bleed detected (phrases not in source like "typically", "as is standard practice") → reject summary and list violations
      - If output path cannot be written → raise IOError with clear message
