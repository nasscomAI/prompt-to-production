# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file and returns its content parsed into a
      list of numbered sections, preserving clause numbers and original wording.
    input: >
      A file path string pointing to a .txt policy document (e.g.
      policy_hr_leave.txt). The file must be UTF-8 encoded plain text with
      numbered clauses (e.g. 2.3, 3.4, 5.2).
    output: >
      A list of dicts, one per clause, each with:
        - clause_id: string (e.g. "2.3") — the original clause number
        - heading: string — section heading if present, else empty string
        - body: string — full verbatim text of the clause, whitespace-normalised
      Sections are returned in source order. The full raw text is also returned
      as a top-level string field `raw_text` for fallback use.
    error_handling: >
      If file_path does not exist or cannot be read: raise FileNotFoundError
      with a descriptive message — do not return partial output.
      If no numbered clauses are detected: return the full raw_text with a
      warning flag `parse_warning: "No numbered clauses detected — verify format"`
      so that summarize_policy can still attempt processing.

  - name: summarize_policy
    description: >
      Takes the structured clause list from retrieve_policy and produces a
      clause-faithful summary in which every clause is present, all conditions
      are preserved, binding verbs are not softened, and no external information
      is added.
    input: >
      The output of retrieve_policy: a list of clause dicts (clause_id, heading,
      body) and the raw_text fallback string.
    output: >
      A plain-text summary string structured as a numbered list, one entry per
      clause, in the format:
        [clause_id] [one or two sentences preserving all conditions and binding
        verbs, or verbatim quote with annotation if summarisation would alter meaning]
      Clauses that cannot be shortened without meaning loss are quoted verbatim
      and appended with the annotation:
        [VERBATIM — summarisation would alter meaning]
    error_handling: >
      If the input clause list is empty: return an error string
      "No clauses to summarise — check retrieve_policy output" and do not
      produce a summary file.
      If an individual clause body is empty or malformed: include the clause_id
      in the summary with the note "[CLAUSE BODY MISSING — manual review required]"
      and continue processing remaining clauses. Do not skip or silently omit it.
