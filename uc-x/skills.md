# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and rigidly indexes the text exactly by document name and specific section numbers to enforce precise citation tracking.
    input: File paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: A structured index safely mapping extracted clauses to their respective source document names and exact section IDs.
    error_handling: Immediately aborts indexing if any of the three required documents are missing or corrupted.

  - name: answer_question
    description: Maps the user's question to the indexed database, outputting a rigid single-source factual answer combined with its direct citation, entirely dodging hallucinations.
    input: The user's unstructured question paired with the extracted document indexes.
    output: A strict unblended factual response citing the exact '[Document, Section]' metadata, OR the verbatim refusal template.
    error_handling: Emits the exact verbatim refusal string immediately if a prompt requests blending topics across multiple documents or attempts to extrapolate undocumented information.
