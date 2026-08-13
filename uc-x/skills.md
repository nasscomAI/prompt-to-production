skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number for efficient single-source lookups.
    input:
      type: file paths
      format: "List of three policy document file paths: policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt"
    output:
      type: object
      format: "Indexed dictionary mapping document name to sections, each section mapped to content: {document_name: {section_number: section_text}}"
    error_handling:
      - If any file is not found, return error with file path
      - If file is empty or unreadable, return error "Could not read policy file"
      - If section numbering cannot be extracted (sections not found or malformed), return error "Could not parse sections"
      - If any required section for test questions is missing, return warning with missing section but continue processing
      - Track which document each section came from — this tracking prevents cross-document blending in answer_question

  - name: answer_question
    description: Searches indexed documents for question answer, returns single-source response with citation OR the exact refusal template if not covered.
    input:
      type: string
      format: "Natural language question about company policy"
    output:
      type: string
      format: "Answer citing document name + section number (e.g., 'HR policy section 2.6 states...') OR the exact refusal template"
    error_handling:
      - If question cannot be answered from any document, return EXACT refusal template: "This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance."
      - If question could be answered from multiple documents but combining them creates a blended answer, return refusal template instead — never blend across documents
      - CRITICAL TEST: Question "Can I use my personal phone for work files from home?" — answer from IT section 3.1 ONLY (email + portal) OR refuse if blending would occur with HR policy — never combine
      - Detect and reject hedging phrases: if answer would start with or contain "while not explicitly covered", "typically", "generally understood", "it is common practice", "presumably", "likely", reject and use refusal template
      - Detect condition dropping: if multi-part requirement found (e.g., "Department Head AND HR Director" for LWP), ensure BOTH parts are stated — never drop one part
      - For question "Who approves leave without pay?" — answer must state "Department Head AND HR Director approval" (both required) — reject if only one approver is stated
      - For question "Can I carry forward unused annual leave?" — answer must cite HR section 2.6 with exact limits and exact forfeiture date
      - For question "Can I install Slack on my work laptop?" — answer must cite IT section 2.3 stating written IT approval requirement
      - For question "What is the home office equipment allowance?" — answer must cite Finance section 3.1 with exact amount and conditions (Rs 8,000 one-time, permanent WFH only)
      - For question "Can I claim DA and meal receipts on the same day?" — answer must cite Finance section 2.6 stating explicit prohibition (NO)
      - Every factual claim in answer must cite source document name + section number — no unsourced statements
      - If question matches multiple sections in same document, choose most specific/relevant section and cite it
      - If question matches sections in different documents requiring combination, return refusal template — do not blend
      - Verify answer is verifiable word-for-word against source text before returning

