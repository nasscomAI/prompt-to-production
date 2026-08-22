skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed into structured numbered sections keyed by clause number.
    input:
      file_path: string — absolute or relative path to the .txt policy document
      (e.g. "../data/policy-documents/policy_hr_leave.txt")
    output: |
      structured_sections: list of objects, each with:
        - clause_id: string  (e.g. "2.3", "5.2")
        - heading: string    (clause title as written in the document)
        - body: string       (full clause text, unmodified)
      Returns an error object if the file is missing or unreadable.
    error_handling: >
      If the file path does not exist or cannot be read, return
      { "error": "FILE_NOT_FOUND", "message": "<path> could not be opened." }
      and do not proceed to summarisation. If the file exists but contains no
      recognisable clause numbering, return
      { "error": "PARSE_FAILURE", "message": "No clause structure detected in <path>." }

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and returns a compliant summary where every clause is represented, binding verbs are preserved, all conditions are retained, and no external information is introduced.
    input: |
      structured_sections: list — non-empty, error-free output of retrieve_policy
      enforcement_rules: list of strings — the rules from the agents.md enforcement block
    output: |
      summary: list of objects, each with:
        - clause_id: string   (matches source clause number)
        - summary_text: string (faithful one-to-two sentence summary, or verbatim
                                quote prefixed with [VERBATIM — CLAUSE X.Y: ...])
        - binding_verb: string (the exact modal/verb preserved from the source)
        - conditions: list of strings (every discrete condition in the clause)
      Plain-text render: a numbered list ordered by clause_id, formatted as
      "[clause_id] <summary_text>"
    error_handling: >
      If structured_sections is empty or contains an error key, return
      { "error": "NO_INPUT", "message": "Cannot summarise — retrieve_policy returned no valid sections." }
      If any single clause cannot be summarised without dropping a condition or
      softening a verb, output that clause verbatim and flag it rather than
      producing a lossy paraphrase.
