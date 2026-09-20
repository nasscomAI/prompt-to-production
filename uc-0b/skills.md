skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content as structured numbered sections.
    input: "input_path (string path to a UTF-8 .txt policy file such as policy_hr_leave.txt)."
    output: "An ordered list of {clause_id (string, e.g. '5.2'), text (full clause wording with wrapped lines joined)} covering every numbered clause found."
    error_handling: "If the file is missing, empty, or contains no numbered clauses (N.N), refuse and do not invent sections. Do not silently skip wrapped continuation lines."

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant clause-referenced summary with no omitted conditions.
    input: "List of {clause_id, text} from retrieve_policy, plus output_path for summary_hr_leave.txt."
    output: "A text file with one summarised (or verbatim-flagged) entry per numbered clause, including clause references."
    error_handling: "If a clause would lose a condition when compressed, quote it verbatim and prefix VERBATIM. If any of the 10 critical clauses is absent from the retrieved set, refuse rather than skip it. Never add scope-bleed phrases."
