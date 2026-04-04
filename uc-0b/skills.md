# skills.md — UC-0B Policy Summarization

skills:
  - name: retrieve_policy
    role: >
      A data ingestion worker that reads plain text policy files and organizes them into an immutable struct.
    intent: >
      To reliably parse a raw `.txt` document and partition it structurally so each numbered section and clause is perfectly isolated for downstream analysis.
    context: >
      Operates on filesystem I/O without any analytical capability. It handles text splitting securely but assumes no authority over what the text means.
    enforcement:
      - "Must not summarize, drop, or alter any vocabulary from the original raw text file."
      - "Must return data strictly in a mapped structure associating clause numbers to their explicit contents."

  - name: summarize_policy
    role: >
      A rigid analytical drafting worker mapping structural policy data into condensed, lossless summaries.
    intent: >
      To iterate securely over structured sections and emit a constrained summary text referencing original clauses while carrying zero risk of condition dropping.
    context: >
      Rests only on the text structure provided. Completely blinded to unwritten expectations, standard HR practices, or outside knowledge.
    enforcement:
      - "Must mandate the inclusion of every identified and numbered active clause in the output."
      - "Must preserve all dual-approver restrictions and conditional sequences identically to the input force."
      - "Must strictly quote verbatim and flag any clause incapable of safe structural compression."
      - "Must omit all colloquial framing including 'typically', 'generally', or 'as is standard practice'."
