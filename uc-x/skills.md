# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexes by document name and section number
    input: none (loads from fixed paths: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt)
    output: dict with keys: document names, values: full content of each policy file as string
    error_handling: If any policy file not found, raises FileNotFoundError with specific path. If file is empty, raises ValueError.
    error_handling_ambiguous: Reports which files could not be loaded without failing completely; continues with available files.

  - name: answer_question
    description: Searches indexed documents, returns single-source answer + citation OR refusal template
    input: question — user query about company policy; indexed_docs — dict from retrieve_documents output
    output: string containing either (a) single-source answer with document + section citation, or (b) refusal template exactly as specified
    error_handling: If question is empty, returns refusal template. If no single document contains the answer (and would require blending), returns refusal template.
    error_handling_ambiguous: If question could be answered from multiple documents, returns answer from first matching document only — never blends claims from two documents. Refuses to combine HR+IT policies when question implies cross-document answer.
