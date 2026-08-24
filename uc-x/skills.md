# skills.md

skills:
  - name: retrieve_documents
    description: >
      Deterministic, non-AI loading step. Reads the three fixed policy
      files from disk and builds a structured index keyed by document
      name and section number. Runs once at startup (and may be re-run
      if a reload is requested); makes no LLM calls and performs no
      interpretation of content — it only parses structure.
    input: >
      No question text. Implicit input is the fixed set of three file
      paths: ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt.
    output: >
      A document index object containing, for each of the three
      documents, an ordered list of sections shaped as
      { document_name, section_number, section_title, section_text }.
      This index is passed as-is to answer_question on every question;
      the documents are already labeled/segmented by source and section
      before any question is asked.
    error_handling: >
      If any of the three files is missing, empty, or fails to read,
      this is a fatal error — the skill must not proceed with a partial
      index (a two-document index makes it impossible to correctly
      distinguish "not covered" from "covered by the missing document",
      and silently continuing risks false refusals or false answers).
      It raises/returns an explicit load error naming the missing
      file(s) rather than starting the CLI with incomplete knowledge.
      If a file loads but contains content that cannot be split into
      numbered sections, the skill still indexes that content under a
      single fallback section (e.g. section_number: "unsectioned")
      rather than dropping it — content is never discarded, only
      citation granularity degrades. It never invents section numbers
      that are not present in the source text.

  - name: answer_question
    description: >
      The only LLM-calling skill. Given one employee question and the
      document index from retrieve_documents, it produces either a
      single-source cited answer or the exact refusal template. Invoked
      once per question in the interactive CLI loop.
    input: >
      { question: string (one user question, raw text as typed),
      documents: the full document index produced by retrieve_documents,
      already labeled by document name and section number }. No other
      context or conversation history is implied unless explicitly
      passed in.
    output: >
      Either: (a) an answer string in which every factual sentence is
      immediately followed by a citation of the form
      "(document_name, Section X.X)", drawing on exactly one document,
      or (b) the refusal template, reproduced verbatim:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
      No other output shape is valid — never a partial answer plus a
      caveat, never an answer with citations from two documents.
    error_handling: >
      Question is not covered by any single document: return the
      refusal template verbatim. Question appears answerable only by
      combining two or more documents (the cross-document trap case):
      treat as not covered and return the refusal template, unless one
      of the documents alone already states a complete answer on its
      own terms — in which case answer from that one document only and
      ignore the other document's tangential mention. Empty or
      non-question input: return the refusal template rather than
      guessing at intent. Document index missing or empty (upstream
      retrieve_documents failure): do not call the model to guess from
      general knowledge; return a distinct system-level error stating
      the knowledge base failed to load, so this failure is never
      confused with an ordinary policy refusal.
