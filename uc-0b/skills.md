skills:
  - name: retrieve_policy
    description: "Load the HR leave policy and return its content as structured numbered sections."
    input: "Path to a UTF-8 plain-text policy file."
    output: "An ordered collection of sections containing clause number and source text."
    error_handling: "Reject a missing, unreadable, or empty file and report sections that cannot be parsed instead of inventing them."

  - name: summarize_policy
    description: "Summarize structured policy sections while retaining every clause and binding condition."
    input: "Structured numbered policy sections from retrieve_policy."
    output: "A clause-referenced text summary covering every source clause and preserving its obligations."
    error_handling: "If a clause is ambiguous or cannot be safely compressed, quote it verbatim and flag it for review; never fill gaps from general knowledge."
