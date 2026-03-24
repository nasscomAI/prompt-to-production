skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk and returns its content as an ordered
      list of numbered sections, each section containing its clause IDs and
      raw text — ready for summarization without any interpretation.
    input: >
      file_path (str) — absolute or relative path to a .txt policy document.
    output: >
      List of dicts: [{section_heading (str), clauses: [{clause_id (str),
      text (str)}]}]. Preserves original document order.
    error_handling: >
      If the file does not exist: raise FileNotFoundError with the path.
      If the file is empty: raise ValueError("Input file is empty — cannot
      summarise without source content.").
      If no numbered clauses are detected (regex finds zero matches): raise
      ValueError("No numbered clauses found in source. Aborting — summarising
      without structure risks silent omission.").

  - name: summarize_policy
    description: >
      Takes the structured sections from retrieve_policy, calls the Groq API
      with a fidelity-first system prompt, and returns a plain-text summary
      where every clause is present, every condition is intact, and every
      binding verb is preserved verbatim.
    input: >
      sections (list) — output of retrieve_policy.
      model (str) — Groq model string, default "llama-3.3-70b-versatile".
      api_key (str) — GROQ_API_KEY from environment.
    output: >
      summary_text (str) — formatted plain text summary with clause references,
      [CONDITIONAL] tags, [VERBATIM] tags where needed, and a
      ## Completeness Check block appended at the end listing each expected
      clause ID as PRESENT/MISSING and each condition as FULL/CONDITION DROPPED,
      with a final verdict of PASS or FAIL.
    error_handling: >
      If the API call fails: surface the HTTP status and error message verbatim.
      Do not return a partial or cached summary.
      If the response contains fewer clause references than the source clause
      count: append a WARNING block listing missing clause IDs before writing
      the output file — do not silently write an incomplete summary.