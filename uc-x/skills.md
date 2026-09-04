skills:
  - name: retrieve_documents
    description: Loads all three policy documents and returns their content indexed by document name and section number for single-source lookup.
    input: >
      A list of three file paths (strings):
        - ../data/policy-documents/policy_hr_leave.txt
        - ../data/policy-documents/policy_it_acceptable_use.txt
        - ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A structured index (dict) keyed by document name, where each value is
      an ordered list of sections containing: section_number (string),
      heading (string), and body (string — unmodified source text).
      The index preserves document boundaries so no cross-document lookups
      are possible without an explicit multi-document query.
    error_handling: >
      If any of the three files is missing or unreadable, halt with a
      descriptive error naming the specific missing file — do not proceed
      with a partial index, as an incomplete index would silently create
      gaps that could cause incorrect refusals.
      If a file is empty, raise an error and halt.
      Never merge sections from different documents into a combined index
      that loses track of which document each section belongs to.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer to the user's question, returning a cited answer or the verbatim refusal template if no single document covers it.
    input: >
      The document index from retrieve_documents (dict) and the user's
      question (string, free text).
    output: >
      Either: (1) a plain-text answer citing the source document name and
      section number for every factual claim (e.g., "per policy_hr_leave.txt
      section 5.2..."), drawn from a single document only; or (2) the
      verbatim refusal template when no single document covers the question:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team]
      for guidance."
    error_handling: >
      Cross-document blending: if answering the question requires combining
      content from two or more documents, the skill must NOT produce a blended
      answer — it must output the verbatim refusal template instead. The
      personal-phone trap (IT section 3.1 + HR remote work tools) is the
      canonical example of this rule.
      Hedged hallucination: if no single document contains the answer, the
      skill must not produce any output containing the phrases "while not
      explicitly covered", "typically", "generally understood", "it is common
      practice", or "it is generally expected" — use the refusal template
      exactly, with no variations or additions.
      Missing citation: every factual claim in an answer must include the
      document name and section number — if a claim cannot be traced to a
      specific section, do not include it in the answer.
      Condition dropping: multi-condition answers (e.g., LWP requires both
      Department Head AND HR Director per policy_hr_leave.txt section 5.2)
      must preserve all named conditions — dropping any condition is
      forbidden even if it makes the answer shorter.
