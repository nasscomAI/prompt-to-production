skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number for precise retrieval.
    input:
      type: file_paths
      format: "list of 3 absolute/relative paths: ['../data/policy-documents/policy_hr_leave.txt', '../data/policy-documents/policy_it_acceptable_use.txt', '../data/policy-documents/policy_finance_reimbursement.txt']"
    output:
      type: indexed_corpus
      format: "JSON object with keys as document names ('policy_hr_leave', 'policy_it_acceptable_use', 'policy_finance_reimbursement'), values as dicts mapping section numbers (e.g., '2.6', '3.1') to full clause text"
    error_handling:
      - If any file missing: raise FileNotFoundError with missing path
      - If file not .txt: raise ValueError
      - If section parsing fails for a document: log warning, include raw content under 'unparsed' key for that document
      - If duplicate section numbers within a document: keep last occurrence, log warning

  - name: answer_question
    description: Searches indexed documents for a single-source answer; returns cited response or exact refusal template.
    input:
      type: question_request
      format: "JSON object with 'question' (string), 'indexed_corpus' (from retrieve_documents output)"
    output:
      type: answer_response
      format: "JSON object with either: {'answer': '...', 'source_document': 'policy_xxx', 'source_section': 'x.x'} OR {'refusal': true, 'template': 'This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.'}"
    error_handling:
      - If question empty: raise ValueError
      - If multiple documents contain relevant claims: refuse with template (prevents cross-document blending)
      - If answer would require combining sections from different documents: refuse with template
      - If hedging phrases detected in generated answer ("while not explicitly covered", "typically", "generally understood", "it is common practice"): reject and return refusal template
      - If no source document + section citation can be attached to answer: refuse with template
      - For "personal phone for work files" question: must return IT policy section 3.1 only OR refusal — never blend with HR policy
