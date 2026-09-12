skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes their content by document name and section number.
    input: >
      A list of three plain-text policy file paths:
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt, and
      ../data/policy-documents/policy_finance_reimbursement.txt.
    output: >
      An index keyed by document name (e.g. policy_it_acceptable_use.txt) and, within
      each document, by section number (e.g. 3.1), where each entry holds the verbatim
      section text of that document.
    error_handling: >
      If a file does not exist or cannot be read, returns an error and does not fabricate
      content. If a file contains no numbered sections, reports that the index could not
      be built for that document. Ambiguous or malformed sections are kept verbatim with
      their document name flagged rather than interpreted. No section is merged with or
      attributed to another document.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: >
      The document index returned by retrieve_documents plus a free-text user question
      (e.g. "Can I use my personal phone to access work files when working from home?").
    output: >
      Either (a) a single-source answer containing the factual claims from exactly one
      document with the document name and section number cited, or (b) the exact refusal
      template verbatim: "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: >
      If the question maps to a single section, returns an answer grounded only in that
      section, cites the document name and section number, and never augments it with
      another document. If the question would require
      combining claims from two or more documents, returns the refusal template — it never
      blends. If the question is not covered by any section or the only truthful response
      would require hedging or inference (e.g. about flexible working culture), returns
      the exact refusal template with no variations, additions, or hedged prefixes like
      "while not explicitly covered" or "typically". If the question or index is empty,
      returns the refusal template rather than guessing.