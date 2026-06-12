skills:

  - name: retrieve_documents
    description: >
      Loads all three authorised policy files from disk and builds an in-memory
      index keyed by document filename and section number so that downstream
      skills can perform fast, citation-accurate lookups.
    input:
      type: file_paths
      format: >
        A list of exactly three absolute or relative file paths pointing to the
        policy documents. Expected values:
          - ../data/policy-documents/policy_hr_leave.txt
          - ../data/policy-documents/policy_it_acceptable_use.txt
          - ../data/policy-documents/policy_finance_reimbursement.txt
        Paths must resolve to readable plain-text files.
    output:
      type: document_index
      format: >
        A structured mapping where each entry has:
          - filename: the basename of the source file (string)
          - sections: a list of objects, each containing:
              - section_number: the section identifier as it appears in the file (string)
              - section_title: the heading text (string)
              - content: the full text of that section (string)
        The index is held in memory for the lifetime of the session and passed
        to answer_question as its sole data source.
    error_handling:
      - condition: One or more file paths do not exist or cannot be read
        action: >
          Raise a LoadError identifying the missing or unreadable file by name.
          Do not proceed with a partial index. Do not substitute content from
          any other source.
      - condition: A file is present but contains no parseable section markers
        action: >
          Raise a ParseError identifying the malformed file. Do not infer
          section boundaries; require the file to be fixed before indexing.
      - condition: Fewer or more than three files are provided
        action: >
          Raise a ConfigError stating the expected file list exactly. Do not
          index an incomplete or extended document set.

  - name: answer_question
    description: >
      Searches the document index produced by retrieve_documents for passages
      relevant to the user's question and returns either a single-source answer
      with a filename-and-section citation, or the mandatory refusal template if
      no single document covers the question.
    input:
      type: question_and_index
      format: >
        An object with two fields:
          - question: the user's natural-language question (string, non-empty)
          - index: the document_index object returned by retrieve_documents
    output:
      type: answer_or_refusal
      format: >
        Exactly one of the following two forms — no mixing, no additional text:

        Form A — Single-source answer:
          A direct answer quoting or closely paraphrasing the relevant passage,
          followed on a new line by a citation in this exact format:
            Source: <filename>, Section <section_number>

        Form B — Refusal template (reproduced verbatim):
          "This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt,
          policy_finance_reimbursement.txt).
          Please contact [relevant team] for guidance."
          Only [relevant team] may be substituted if the correct team can be
          determined unambiguously from the indexed documents; otherwise the
          placeholder is left as-is.
    error_handling:
      - condition: Relevant passages are found in more than one document and
          combining them would alter the meaning or grant permissions beyond
          what any single document states (cross-document blending risk)
        action: >
          Return Form B — the refusal template — immediately. Do not synthesise
          a blended answer. Do not cite multiple sources in a single response.
      - condition: The question matches content in one document but the passage
          is conditional (requires approval, states a limit, names an approver,
          or specifies a date) and any condition would need to be omitted to
          form a clean answer
        action: >
          Include all conditions in the answer without exception. An answer that
          omits a condition is treated as a failed output; return Form B instead
          if the conditions cannot be stated clearly.
      - condition: No passage in any indexed document addresses the question
        action: >
          Return Form B — the refusal template — verbatim. Do not use hedging
          phrases such as "while not explicitly covered", "typically",
          "generally understood", or "it is common practice".
      - condition: The question is empty, null, or not a string
        action: >
          Return a validation error prompting the caller to supply a non-empty
          question string. Do not attempt a document search.
      - condition: The index object is missing, empty, or was not produced by
          retrieve_documents
        action: >
          Raise a DependencyError instructing the caller to run
          retrieve_documents successfully before calling answer_question.
