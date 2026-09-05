skills:
  - name: retrieve_policy
    description: Loads a .txt HR policy file and returns its content as structured numbered sections keyed by clause identifier.
    input:
      type: file
      format: plain text (.txt)
      path: string — absolute or relative path to the policy document (e.g. ../data/policy-documents/policy_hr_leave.txt)
    output:
      type: dict
      fields:
        - document_title: string — title extracted from the document header
        - sections: list — each item contains {clause_id: string, heading: string, text: string} for every numbered clause (e.g. 2.3, 5.2)
      notes: clause_id values must match the numbering in the source (section.subsection format)
    error_handling:
      - "if file path does not exist: raise FileNotFoundError with the full attempted path — do not proceed"
      - "if file exists but is empty or unreadable: raise ValueError stating the file contains no policy content — do not proceed"
      - "if file content cannot be parsed into numbered sections: raise ValueError stating which section numbering failed — do not return a partial structure"
      - "if any of the 10 ground-truth clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are absent from the parsed output: raise ValueError naming the missing clause IDs — do not pass incomplete structure to summarize_policy"

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving every binding obligation and all multi-condition requirements per agents.md enforcement rules.
    input:
      type: dict
      fields:
        - sections: list — structured numbered sections as returned by retrieve_policy
      notes: must contain all clauses from the source document; summarize_policy must not fetch external content
    output:
      type: file
      format: plain text (.txt)
      path: string — output file path (e.g. summary_hr_leave.txt)
      content_structure: each entry is one clause summary line formatted as "[clause_id] summary text" with binding verbs and all conditions preserved
      notes: clauses quoted verbatim must be suffixed with [VERBATIM]
    error_handling:
      - "if sections input is empty or None: raise ValueError stating no policy sections were provided — do not call the LLM"
      - "if any ground-truth clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is missing from the input sections: raise ValueError naming the missing clauses — do not produce a partial summary"
      - "if the LLM output omits any numbered clause from the source: reject the response, retry once with an explicit correction prompt listing the missing clause IDs, and if still incomplete raise ValueError — do not write the output file"
      - "if the LLM output drops a condition from a multi-condition obligation (e.g. clause 5.2 names only one approver): reject the response, retry once naming the dropped condition, and if still incomplete quote clause 5.2 verbatim with [VERBATIM] flag rather than returning a weakened summary"
      - "if the LLM output contains scope-bleed phrases not present in the source (e.g. 'as is standard practice', 'typically in government organisations', 'employees are generally expected to'): reject the response, retry once with an explicit scope-bleed correction, and if still present raise ValueError — do not write the output file"
      - "if the LLM softens a binding verb (must → may/should, not permitted → generally discouraged): reject the response and retry once — if still softened, quote the affected clause verbatim with [VERBATIM] flag"
      - "if the LLM call raises an exception (timeout, API error, rate limit): do not write a partial summary file — propagate the error to the caller with a message stating summarization failed"
      - "if output file path directory does not exist or is not writable: raise IOError before writing — do not silently discard results"
