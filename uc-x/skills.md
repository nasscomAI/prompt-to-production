skills:
  - name: retrieve_documents
    description: Ingests the three CMC policy files (HR, IT, Finance) and builds an in-memory clause and section index mapped by document filename and section identifier.
    input: List or directory containing policy files ('policy_hr_leave.txt', 'policy_it_acceptable_use.txt', 'policy_finance_reimbursement.txt').
    output: Indexed dictionary mapping document identifiers and section numbers to normalized text passages and metadata.
    error_handling: Verifies accessibility of all three policy files; raises FileNotFoundError if any policy document is missing.

  - name: answer_question
    description: Resolves staff questions by searching the indexed documents, identifying the single most relevant authoritative section, synthesizing an answer with exact citations, or returning the standard refusal template.
    input: User question string and indexed documents structure from retrieve_documents.
    output: Structured response string containing either the cited answer with document name and section reference, or the exact refusal template.
    error_handling: Strictly prohibits cross-document blending. If information spans across documents without a single authoritative section or if the question is unaddressed (e.g. flexible working culture), returns the required refusal template without hedging phrases.
