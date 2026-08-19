# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into a structured list of numbered sections, preserving clause numbers, binding verbs, and all sub-conditions exactly as written.
    input: >
      - file_path (string): absolute or relative path to the policy .txt file.
      Example: "../data/policy-documents/policy_hr_leave.txt"
    output: >
      A list of section objects, each containing:
        - clause_id (string): the clause number as it appears in the document (e.g. "2.3", "5.2")
        - heading (string): the clause heading or title if present, else blank
        - body (string): the full verbatim text of the clause, including all sub-conditions
        - binding_verb (string): the primary obligation verb found (must / will / requires / not permitted / may), else blank
      Example: [{ "clause_id": "2.3", "heading": "Advance Notice", "body": "Employee must give 14 days advance notice...", "binding_verb": "must" }]
    error_handling: >
      If file_path does not exist — raise FileNotFoundError with the path.
      If the file is empty — raise ValueError: "Policy file is empty."
      If no numbered clauses are detected — raise ValueError: "No numbered clauses found — check document format."

  - name: summarize_policy
    description: Takes the structured section list from retrieve_policy and produces a clause-by-clause summary that preserves every obligation, all conditions, and binding verbs — flagging any clause that cannot be paraphrased without meaning loss.
    input: >
      - sections (list): the structured section list returned by retrieve_policy.
      - output_path (string): path to write the summary .txt file.
    output: >
      A .txt file at output_path where each clause appears as:
        [clause_id] [heading if present]
        Summary: <one or two sentences preserving all conditions and binding verbs>
        Flag: VERBATIM_REQUIRED  ← only if paraphrase would lose meaning

      Stdout summary line: "Summarised N clauses. VERBATIM_REQUIRED: M."
    error_handling: >
      If sections list is empty — print error and exit with code 1.
      If a clause body is blank — include the clause_id in output with body: "[EMPTY CLAUSE — review source document]" and flag: VERBATIM_REQUIRED.
      Never silently skip a clause — every clause_id from the input must appear in the output.
