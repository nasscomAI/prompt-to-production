# skills.md

skills:
  - name: "retrieve_policy"
    description: "Loads the .txt policy file and parses it into structured numbered sections for easier traversal."
    input: "Path to the .txt policy document."
    output: "A structured map of clause numbers to their verbatim text."
    error_handling: "If a file is missing or unreadable, log an error and halt; do not attempt to summarize a partial document."

  - name: "summarize_policy"
    description: "Applies R.I.C.E. enforcement rules to summarize structured policy sections into a compliant audit-ready summary."
    input: "Structured map of policy clauses (from retrieve_policy)."
    output: "A summary document citing all clause references and preserving all multi-condition obligations."
    error_handling: "If a clause is missing a core obligation or condition during summarization, revert to verbatim quotation with a [POTENTIAL MEANING LOSS] tag."
