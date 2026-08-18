skills:
  - name: retrieve_documents
    description: >
      Loads all three CMC policy files and indexes them by document name and
      section number for single-source retrieval.
    input: >
      Directory or explicit paths to policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      Index map: document filename → list of sections {section_id, heading,
      text}, with full source wording preserved (no paraphrase at index time).
    error_handling: >
      If any of the three files is missing, unreadable, or empty, raise a clear
      load error and refuse Q&A — do not substitute other documents or invent
      sections. Do not silently drop malformed clauses; keep them indexed so
      answer_question can cite or refuse.

  - name: answer_question
    description: >
      Searches the indexed documents and returns a single-source answer with
      citation, or the exact refusal template when uncovered or ambiguous
      across documents.
    input: >
      Natural-language staff question (string) plus the document index from
      retrieve_documents.
    output: >
      Either (1) answer text drawn from exactly one document, including
      document filename + section number citation and all conditions from that
      section, or (2) the refusal template verbatim.
    error_handling: >
      If no section matches, or matching would require combining two documents
      (cross-document blending), return the refusal template exactly — never
      hedge. If a matched section has multiple conditions, preserve all of
      them; dropping one (e.g. only one LWP approver) is a failure. Reject
      any draft that introduces hedging phrases. Empty questions → prompt
      retry or refuse without inventing content.
