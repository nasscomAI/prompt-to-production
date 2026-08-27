# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy documents from disk, parses each into indexed sections keyed by document name and section number, and returns a unified index ready for single-source lookup.
    input: >
      A list of three file paths (strings), in any order:
        - policy_hr_leave.txt
        - policy_it_acceptable_use.txt
        - policy_finance_reimbursement.txt
      All three must be provided; partial loading is not permitted.
    output: >
      An opaque document index dict — callers must not inspect its structure
      directly. Pass the returned value unchanged to answer_question.

      Internally the index is structured as:
        {
          "<filename>": {
            "<section_id>": {"display": "<body text>", "heading": "<parent heading>"},
            "_raw": {"display": "<full raw text>", "heading": ""},
            ...
          },
          "_idf": { "<word>": <float>, ... }
        }
      Keys at the document level are bare filenames (not full paths) so citations
      are stable. Sections are parsed by numbered clause pattern (e.g. "3.1", "5.2").
      The "_idf" key holds IDF weights computed across all sections in all three
      documents for use by answer_question scoring.
      The "_raw" key within each document entry stores the verbatim full text
      for fallback verification.
    error_handling: >
      If any of the three files cannot be found, raise FileNotFoundError
      naming the missing file — do not proceed with a partial index.
      If a file is empty or contains no parseable numbered sections,
      raise ValueError: "No numbered sections found in <filename> —
      verify document format before indexing."
      Never return an index with fewer than three documents.

  - name: answer_question
    description: Searches the document index produced by retrieve_documents for the single best-matching section, returns a cited answer from that one document only, or returns the exact refusal template if the question is not covered.
    input: >
      Two values:
        index    — the document index dict returned by retrieve_documents
        question — a plain-text string containing the employee's question
    output: >
      A plain-text answer string in one of two forms:

      Form A — question is covered:
        The factual answer, followed on a new line by:
        "Source: <filename>, section <section_id>"
        Example:
          "Leave encashment during service is not permitted under any
           circumstances.
           Source: policy_hr_leave.txt, section 7.2"

      Form B — question is not covered in any document:
        Exactly: "This question is not covered in the available policy
        documents (policy_hr_leave.txt, policy_it_acceptable_use.txt,
        policy_finance_reimbursement.txt). Please contact [relevant team]
        for guidance."
        No variations, no hedging, no partial answer before the refusal.
    error_handling: >
      If the index is empty or missing any of the three documents, refuse
      and return: "Document index is incomplete — retrieve_documents must
      be called successfully with all three policy files before answering."
      If the question is an empty string, return the refusal template —
      do not attempt a search on empty input.
      If the best-matching section is from two documents with equal
      confidence, return only the refusal template — never blend or guess
      which document takes precedence.
      Never use hedging phrases: "while not explicitly covered",
      "typically", "generally understood", "it is common practice",
      or any equivalent — if the document does not state it, refuse.
