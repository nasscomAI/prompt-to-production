# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files from their specified paths and returns a
      structured index keyed by document name and section number, with
      section text stored verbatim and no content merged across documents.
    input:
      type: list
      format: >
        A fixed list of three file paths: ../data/policy-documents/
        policy_hr_leave.txt, ../data/policy-documents/
        policy_it_acceptable_use.txt, and ../data/policy-documents/
        policy_finance_reimbursement.txt; all three paths are required and
        must resolve to readable UTF-8 encoded plain-text files containing
        numbered sections in the format [section].[clause] followed by
        policy text.
    output:
      type: object
      format: >
        A nested index object with three top-level keys, one per document
        name (policy_hr_leave.txt, policy_it_acceptable_use.txt,
        policy_finance_reimbursement.txt); each top-level key maps to a
        further key-value object where each key is a section number string
        (e.g. "2.6", "3.1", "5.2") and each value is the verbatim section
        text as it appears in the source file with no modifications,
        paraphrasing, or cross-document merging; document boundaries must
        be preserved such that no section text from one document appears
        under another document's key.
    error_handling:
      file_not_found: >
        If any of the three required file paths does not resolve to a
        readable file, halt immediately and raise an error naming every
        missing file — do not return a partial index covering only the
        available files, as a partial index would allow answer_question to
        operate without disclosure that one or more documents are missing.
      missing_all_files: >
        If none of the three files can be loaded, halt and raise a critical
        error before any index object is constructed — do not return an
        empty index that answer_question could silently treat as a loaded
        state.
      unreadable_encoding: >
        If any file cannot be decoded as UTF-8, halt and raise an encoding
        error identifying the affected file — do not attempt lossy decoding
        that could corrupt section text and produce subtly wrong answers.
      no_sections_detected: >
        If a successfully loaded file yields no identifiable numbered
        section structure, emit a WARNING naming the affected document
        before returning the index — do not silently include it as an
        empty document entry, as answer_question would then search it
        without finding any citable sections.
      cross_document_merge_attempt: >
        If any processing step would cause section text from one document
        to be stored under another document's key, halt and raise a
        structural error — document identity must be preserved exactly as
        loaded and must never be normalised or deduplicated across sources.

  - name: answer_question
    description: >
      Searches the structured document index for content relevant to a
      natural language question, returns a single-source answer with
      document name and section number citation if a clear single-source
      match exists, or returns the refusal template verbatim if the
      question is not covered or if relevant content spans more than one
      document.
    input:
      type: object
      format: >
        An object with two fields: question (a non-empty natural language
        string representing the user's policy query) and index (the full
        nested document index object returned by retrieve_documents,
        containing all three documents keyed by document name and section
        number).
    output:
      type: object
      format: >
        An object with three fields: answer (a string containing either a
        factual response grounded in a single document section or the
        refusal template exactly as specified), source_document (the
        document name string matching the key in the index from which the
        answer was drawn, or null if the refusal template was issued), and
        section (the section number string from which the answer was drawn,
        or null if the refusal template was issued); the answer field must
        never be empty.
    error_handling:
      question_not_in_any_document: >
        If no section across any of the three documents contains content
        that directly addresses the question, the answer field must be set
        to exactly the following string and no other: "This question is not
        covered in the available policy documents (policy_hr_leave.txt,
        policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
        Please contact [relevant team] for guidance." — paraphrasing,
        shortening, or adding to this template is a violation.
      cross_document_match: >
        If relevant content is found in more than one document and
        combining it would be required to form a complete answer, the skill
        must not blend the sources — it must either return the single-source
        IT policy section 3.1 answer alone when the personal-phone question
        is asked, or issue the refusal template if genuine ambiguity exists
        across documents; cross-document blending is a violation regardless
        of how relevant both sources appear.
      hedged_language_detected: >
        If the draft answer text contains any of the following phrases —
        "while not explicitly covered", "typically", "generally understood",
        "it is common practice" — the skill must reject the draft, strip
        the offending phrase, and either rewrite from source text only or
        issue the refusal template; no hedged language may appear in the
        final answer field.
      condition_drop_on_multi_condition_clause: >
        If the matched section contains a multi-condition obligation, all
        conditions must appear in the answer — for HR section 5.2 both
        Department Head and HR Director must be named; for Finance section
        2.6 the explicit prohibition must be stated as such and not softened;
        dropping any condition is a violation and the skill must rewrite
        the answer to restore the missing condition before returning output.
      missing_citation: >
        If a factual claim is present in the answer field but source_document
        or section is null or empty, the skill must halt and populate both
        citation fields before returning — an answer with a factual claim
        and no citation is a violation.
      empty_index: >
        If the index field of the input is empty or missing, halt and raise
        an error stating that no documents are loaded — do not attempt to
        answer from memory or general knowledge.
      empty_question: >
        If the question field is an empty string or null, halt and raise a
        validation error requesting a non-empty question — do not return a
        default or example answer.
