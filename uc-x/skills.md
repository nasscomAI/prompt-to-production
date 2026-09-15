skills:
  - name: retrieve_documents
    description: Ingests the 3 policy text files from the data directory and extracts structured document sections with their parent filenames and section headers.
    input: File paths or directory containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: In-memory structured collection of policy sections indexed by filename, section identifier, and section text.
    error_handling: Raises FileNotFoundError if any of the three policy files are missing.

  - name: answer_question
    description: Evaluates a user query against the indexed policy documents, selects a single authoritative source section, and returns a verified answer with section citations or emits the verbatim refusal template.
    input: User question as a string and the loaded document context.
    output: String containing a single-source factual answer with document and section citation, OR the exact verbatim refusal template.
    error_handling: If no matching section exists, or if answering requires blending multiple documents with conflicting scopes, automatically triggers the standard refusal template.