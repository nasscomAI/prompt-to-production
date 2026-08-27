# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three authorized policy text files and indexes their content strictly by document name and section number.
    input: File paths to the three policy documents (e.g., policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: A rigid, structured index mapping each literal text block to its specific source document and section identifier.
    error_handling: If any document fails to load or cannot be indexed with explicit section numbers, immediately log an error and refuse to initialize.

  - name: answer_question
    description: Searches the indexed documents for exact factual matches to answer a user's question, returning either a single-source cited answer or the mandated refusal template.
    input: A string representing the user's question and the indexed document context.
    output: A string containing the exact answer with explicit "Document Name + Section Number" citations, OR the verbatim refusal template.
    error_handling: If an answer requires blending information across multiple distinct documents, immediately trigger the verbatim refusal template to avoid unauthorized synthesis.
