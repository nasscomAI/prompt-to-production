# skills.md — UC-X Ask My Documents

# Implements: agents.md · core failure modes: cross-document blending, hedged hallucination, condition dropping

skills:
  - name: retrieve_documents
    description: >
      Loads exactly the three UTF-8 policy files listed in agents.md io_contract, validates
      readability, and builds an index keyed by logical document name (file basename) and section
      identifiers (numbered sections such as 2.6, 3.1, 5.2) so downstream answers can cite
      document + section without scanning raw text on every turn. No merging of files — each source
      stays separable for single-source answering.
    input: >
      Optional explicit paths; defaults to policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt under ../data/policy-documents/ per agents.md.
    output: >
      A structure usable by answer_question: per-document raw text (or equivalent), plus a section
      index mapping (document_name, section_id) → span text, preserving wording needed for multi-party
      rules (e.g. AND between approvers in HR 5.2).
    error_handling: >
      If any file is missing, empty, or not UTF-8, fail with a clear error — do not substitute web or
      guessed policy text. If section parsing is ambiguous, still expose raw document text so
      answer_question can refuse rather than invent structure.

  - name: answer_question
    description: >
      Takes a user natural-language question plus retrieve_documents output, retrieves evidence from
      indexed sections, and returns either (1) a single-source grounded answer with document name +
      section number for every factual claim, or (2) the agents.md refusal_template verbatim when the
      corpus does not support an answer — with no hedging phrases. Must not merge claims across
      documents into one narrative. For agents.md cross_document_trap, prefer IT-only section 3.1 or
      refusal; never blend HR+IT into a new permission.
    input: >
      User question string; indexed documents from retrieve_documents. Optional trace flags for CLI
      debugging — must not pull facts from outside the three files.
    output: >
      Either { answer_text, citations: list of { document, section } } with at least one citation per
      factual sentence, or { refusal: true, text: <exact refusal_template> }. Forbidden in answer_text:
      listed hedging phrases in agents.md enforcement; cross-document synthesis when that invents
      obligations; dropped AND conditions on approvers or similar multi-requirement rules.
    error_handling: >
      If retrieval finds no supporting section, emit refusal_template unchanged—no paraphrase.
      If question could tempt blending (trap), return IT-sourced narrow answer or refusal per
      agents.md cross_document_trap. If inputs are empty or malformed, refuse safely with template or
      explicit error — never guess policy content.

alignment:
  agent_spec: "agents.md"
  enforcement: >
    retrieve_documents MUST keep documents separable and section-addressable. answer_question MUST
    cite document + section for every factual claim; MUST use refusal_template exactly when not in
    corpus; MUST NOT combine two documents into one answer; MUST NOT use banned hedging phrases; MUST
    preserve compound conditions (e.g. both approvers in HR 5.2).
