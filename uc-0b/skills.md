skills:
  - name: retrieve_policy
    description: >
      Load a plain-text HR policy and convert it into an ordered, traceable
      collection of numbered sections without interpreting or altering its content.
    input: >
      A readable path to a UTF-8 .txt policy document.
    output: >
      An ordered list of section records. Each record contains the source clause
      number and its complete verbatim text. Headings and unnumbered introductory
      text are retained separately so no source content is silently discarded.
    error_handling: >
      Reject missing, unreadable, empty, non-text, or structurally unparseable
      input. Identify the exact file or parsing problem and do not invent clause
      numbers, repair incomplete text, or infer missing content.

  - name: summarize_policy
    description: >
      Produce a concise clause-by-clause policy summary while preserving every
      obligation, condition, exception, approver, threshold, deadline, consequence,
      prohibition, binding verb, and clause reference.
    input: >
      The ordered structured sections returned by retrieve_policy, with each
      source clause number paired with its complete verbatim text.
    output: >
      A plain-text summary containing one traceable entry for every numbered
      source clause. Each entry retains its clause number and original obligation
      strength. Any clause that cannot be compressed without meaning loss is
      reproduced verbatim and flagged as a verbatim quotation. Before returning,
      the skill verifies complete clause and condition coverage, including special
      checks for clauses 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
    error_handling: >
      Refuse to guess when sections are missing, duplicated, incomplete, ambiguous,
      or lack traceable clause numbers. Report the affected clauses. Never add
      external knowledge or silently drop a condition; quote the source clause
      verbatim and flag it when faithful summarization is not possible.
