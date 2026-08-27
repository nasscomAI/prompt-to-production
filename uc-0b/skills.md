# skills.md — UC-0B Policy Summary

skills:
  - name: retrieve_policy
    description: Loads the HR Leave Policy .txt file and returns content as structured numbered sections.
    input: File path (string) to the policy document.
    output: Dictionary keyed by clause number (e.g., "2.3", "5.2") mapping to clause text (string). Returns full document header/metadata as separate field.
    error_handling: >
      If file not found: raise FileNotFoundError with message specifying the file path.
      If file is empty: raise ValueError with message "Policy file is empty".
      If file is not policy_hr_leave.txt: refuse with "Only policy_hr_leave.txt is supported for UC-0B".

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with all clause references preserved.
    input: Dictionary of clause_number -> clause_text from retrieve_policy.
    output: String containing formatted summary with each clause numbered and binding verb bolded or marked.
    error_handling: >
      If required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are missing: flag with [MISSING-CLAUSE] prefix and include verbatim quote from source if available.
      If a clause text is too short to summarise meaningfully: quote verbatim and flag with [QUOTED-FLAG].
