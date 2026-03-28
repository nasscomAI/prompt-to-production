# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes content by document name and section number for exact retrieval.
    input: File paths for policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Structured index keyed by document name and section number, with section text for retrieval.
    error_handling: If any required document is missing or unreadable, return a hard error and stop. If a section cannot be parsed, keep raw text and flag parsing issue for review.

  - name: answer_question
    description: Searches indexed documents and returns either a single-source answer with citation(s) or the exact refusal template.
    input: User question string and document index from retrieve_documents.
    output: Either a single-source answer with document name plus section citation for each factual claim, or this exact refusal text: This question is not covered in the available policy documents (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt). Please contact [relevant team] for guidance.
    error_handling: If question requires combining claims across documents or no direct support exists in the index, return the exact refusal template with no variation and no hedging language.
