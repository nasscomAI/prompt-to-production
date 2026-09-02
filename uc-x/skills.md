# skills.md - UC-X Document Question Answerer

skills:
  - name: retrieve_documents
    purpose: >
      Load all three policy files and index their complete source content by
      exact document name and original section number.
    input:
      type: list of file paths
      files:
        - "../data/policy-documents/policy_hr_leave.txt"
        - "../data/policy-documents/policy_it_acceptable_use.txt"
        - "../data/policy-documents/policy_finance_reimbursement.txt"
    output:
      type: indexed document collection
      structure: "document filename -> section number -> source wording"
      requirements:
        - "Include all three documents."
        - "Preserve exact document filenames and original section numbers."
        - "Preserve source wording, conditions, limits, actors, thresholds, deadlines, exceptions, consequences, and prohibitions."
    expected_behavior:
      - "Read each supplied policy file as an independent source."
      - "Index every numbered section under its source document name and section number."
      - "Keep content from different documents separate and attributable."
      - "Do not paraphrase, merge, omit, or supplement source content during retrieval."
    constraints:
      - "Do not add external policy information or inferred sections."
      - "Do not treat a fact in one document as if it appeared in another document."
    error_handling:
      - "If a file cannot be read, report the retrieval error rather than inventing or reconstructing its content."
      - "If section numbering is missing or malformed, preserve the raw content and identify the indexing problem."

  - name: answer_question
    purpose: >
      Search the indexed documents and return either a single-source answer
      with an exact document and section citation or the exact refusal template.
    input:
      type: user question
      source: "indexed output from retrieve_documents"
    output:
      type: answer text
      allowed_forms:
        - "A source-faithful answer using claims from exactly one document, citing its exact filename and section number."
        - |-
          This question is not covered in the available policy documents
          (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
          Please contact [relevant team] for guidance.
    expected_behavior:
      - "Select one source document and answer only from the relevant section or sections in that document."
      - "Cite the exact source document filename and section number for every factual claim."
      - "Preserve all conditions and limits from the cited source."
      - "For the personal-phone question, use only IT section 3.1 if it directly answers the question; otherwise return the exact refusal template."
      - "Return the exact refusal template, with no variations or additional claims, when the question is not covered or single-source support is insufficient."
    constraints:
      - "Never combine claims from policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt in one answer."
      - "Never use hedging phrases such as while not explicitly covered, typically, generally understood, or it is common practice."
      - "Do not invent facts, permissions, prohibitions, exceptions, thresholds, deadlines, or external policy language."
      - "Do not transfer HR remote-work claims into the IT personal-device answer."
    error_handling:
      - "If no single source section directly answers the question, return the exact refusal template."
      - "If indexed documents conflict or answering would require combining documents, return the exact refusal template."
      - "If the question is empty or invalid, return the exact refusal template."
