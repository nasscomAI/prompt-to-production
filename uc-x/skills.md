skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and decimal section number (e.g. 3.1, 2.6), so answers can be traced to a single source.
    input:
      type: list of file paths
      format: "Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output:
      type: index
      format: "{document_name: [{section_id: str, text: str}, ...]} — one list of sections per document, each section keyed by its number"
    error_handling: >
      If any of the 3 files is missing, raise a clear error naming which
      file is absent and stop — do not proceed with a partial index. If a
      document contains no detectable section numbers, index its full
      content as section '0' rather than silently dropping it.

  - name: answer_question
    description: Searches the indexed documents for the single document/section that answers a question, and returns either a cited single-source answer or the exact refusal template.
    input:
      type: string + index
      format: "question (str), plus the document index from retrieve_documents"
    output:
      type: dict
      format: "{answer: str, source_document: str or None, section: str or None, refused: bool}"
    error_handling: >
      If matching sections are found in more than one document, do not
      merge them into an answer — set refused=True and return the exact
      refusal template. If no matching section is found in any document,
      also set refused=True and return the exact refusal template. Never
      fall back to general knowledge to fill the gap.
