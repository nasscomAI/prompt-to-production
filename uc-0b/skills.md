skills:
  - name: retrieve_policy
    description: Loads the supplied UTF-8 HR policy text file and returns its numbered clauses as structured sections.
    input: "A readable UTF-8 .txt policy file path containing the HR leave policy and its numbered clauses."
    output: "A structured list of sections, where each item contains the clause number and exact clause text in source order; ambiguous or malformed structure is rejected and reported for review."
    error_handling: "Reject missing, unreadable, non-UTF-8, empty, duplicate-numbered, or structurally ambiguous input. Do not infer missing clauses or silently attach ambiguous text to a neighboring clause."

  - name: summarize_policy
    description: Produces a clause-referenced HR policy summary from validated structured policy sections without changing their meaning.
    input: "A structured list of numbered policy sections containing clause numbers and source text returned by retrieve_policy."
    output: "A UTF-8 plain-text summary containing one identifiable entry for every source clause, with all conditions, thresholds, deadlines, approvers, exceptions, consequences, and binding language preserved."
    error_handling: "Reject missing or incomplete sections and report which clause references are absent. Never fill gaps from outside knowledge. If compression could change meaning, quote the affected clause verbatim and add an explicit review flag; do not soften or omit obligations."
