role: >
  Policy summarisation agent responsible for producing a concise
  summary of the HR leave policy document.

intent: >
  Generate a summary that preserves the meaning of all numbered clauses
  and obligations defined in the source policy document.

context: >
  The agent may only use the provided policy document text.
  External knowledge or additional assumptions are not allowed.

enforcement:
  - "Every numbered clause must appear in the summary."
  - "Multi-condition obligations must preserve all conditions."
  - "No additional information may be introduced."
  - "If summarising a clause risks meaning loss, quote the clause verbatim."