skills:

  - name: load_documents
    description: Load and validate all supplied policy documents before answering questions.
    input: Three UTF-8 text files containing HR Leave, IT Acceptable Use, and Finance Reimbursement policies.
    output: Validated collection of documents containing document name, path, and normalized text content.
    error_handling: If a required document is missing, unreadable, empty, or malformed, report the problem and do not invent replacement content.

  - name: retrieve_policy_evidence
    description: Find the most relevant policy sections from the supplied documents for a user's question.
    input: User question as text plus the validated policy document collection.
    output: Ranked evidence containing source document, matching section or clause, supporting text, and relevance information.
    error_handling: If no sufficiently relevant evidence is found, return a not-found result and do not generate an unsupported answer.

  - name: answer_from_evidence
    description: Produce a grounded answer using only the retrieved policy evidence while preserving all material conditions.
    input: User question plus retrieved policy evidence.
    output: Concise answer containing the answer, source document, relevant section or clause, and a clear not-found statement when evidence is insufficient.
    error_handling: If evidence is conflicting, ambiguous, or incomplete, identify the uncertainty and ask for clarification or refuse to guess rather than inventing a policy rule.