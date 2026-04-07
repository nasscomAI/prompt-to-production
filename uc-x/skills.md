# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files (HR, IT, Finance), indexes content by document name and section number for searchable retrieval.
    input: |
      - base_path (string) — path to policy-documents directory
    output: |
      Dictionary containing:
      {
        "documents": {
          "policy_hr_leave.txt": {
            "title": string,
            "reference": string,
            "sections": {
              "1": {"title": "PURPOSE AND SCOPE", "clauses": {"1.1": "text...", "1.2": "text..."}},
              "2": {"title": "ANNUAL LEAVE", "clauses": {"2.1": "text...", ...}},
              ...
            }
          },
          "policy_it_acceptable_use.txt": {...},
          "policy_finance_reimbursement.txt": {...}
        },
        "total_documents": 3,
        "total_sections": int,
        "total_clauses": int
      }
    error_handling: |
      - If base_path does not exist → raise FileNotFoundError
      - If any of the 3 required policy files is missing → raise ValueError listing missing files
      - If a file is empty or has no numbered clauses → raise ValueError for that file
      - If document parsing fails → log warning but continue with other documents

  - name: answer_question
    description: Searches indexed documents for answer to user question. Returns single-source answer with citation OR refusal template. NEVER blends information from multiple documents.
    input: |
      - documents (dict) — output from retrieve_documents
      - question (string) — user's question in natural language
    output: |
      Dictionary containing:
      {
        "answer": string — direct answer to question OR refusal template,
        "source_document": string — filename of source document (or "NONE" if refusal),
        "source_section": string — section number (e.g., "2.6") or "NONE",
        "citation": string — "[policy_X.txt, Section Y.Z]" format,
        "is_refusal": boolean — true if using refusal template
      }
      
      REFUSAL TEMPLATE (exact wording, no variations):
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: |
      - If question matches content from MULTIPLE documents → DO NOT BLEND. Either:
        (a) Answer from ONE document only with explicit citation, OR
        (b) Use refusal template if combination creates ambiguity
      - If question uses hedging language → still provide factual answer or refusal, never hedge back
      - If question is empty → return error "Please enter a question"
      - If no matching content found in any document → use refusal template exactly, no variations
      - PROHIBITED phrases in answer: "while not explicitly covered", "typically", "generally understood", "it is common practice", "usually", "in most cases"
