skills:
  - name: retrieve_policy
    description: Loads the supplied plain-text HR policy file and returns its contents as structured numbered sections while preserving clause references and source wording.
    input:
      type: file path
      format: plain-text .txt policy document
    output:
      type: structured sections
      format: numbered policy sections containing clause references and source text
    error_handling: Reject missing, unreadable, empty, or non-text input. Do not infer or reconstruct missing policy content. Report malformed or missing clause numbering rather than silently omitting content.

  - name: summarize_policy
    description: Converts structured policy sections into a concise clause-referenced summary while preserving every obligation, condition, limitation, approval requirement, deadline, exception, and prohibition.
    input:
      type: structured policy sections
      format: numbered sections containing clause references and source text
    output:
      type: text
      format: clause-referenced policy summary
    error_handling: If a clause cannot be summarized without changing its meaning, quote it verbatim and flag it. Never silently omit a clause, drop a condition from a multi-condition obligation, weaken binding language, or introduce information not contained in the source.
