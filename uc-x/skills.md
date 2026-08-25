# skills.md

skills:
  - name: retrieve_documents
    description: Loads the three CMC policy files and indexes them by document name and section number.
    input: None — reads ../data/policy-documents/{policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt} (UTF-8).
    output: Index {document_name -> {section_number -> {title, {clause_number -> clause_text}}}}; multi-line clauses are joined; divider lines (═+) and blanks are skipped.
    error_handling: Missing or unreadable file aborts with a clear error naming the file; unrecognised lines are ignored only when blank or a divider; lines appearing before the first numbered heading are treated as metadata and ignored.

  - name: answer_question
    description: Searches the indexed documents for a single-source answer and returns cited verbatim clauses or the exact refusal template.
    input: Question string in natural language.
    output: Either "[document_name §X.Y] <verbatim clause text>" lines from exactly ONE document (top <=3 clauses scoring above 75% of the best score, presented in document order), or the refusal template verbatim with [relevant team] filled deterministically (best-scoring document's team; literal placeholder if zero signal).
    error_handling: Refuses (emits the refusal template) when coverage of query terms by the best clause is below 0.34 or fewer than 2 distinct terms match; fails closed to the refusal template if the assembled answer would contain a hedge phrase ('while not explicitly covered', 'typically', 'generally understood', 'it is common practice') or citations spanning more than one document.
