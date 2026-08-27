skills:
  - name: retrieve_documents
    description: >
      Loads all three policy text files from the data directory and indexes their
      contents by document name and section number for precise retrieval.
    input: >
      - No input parameters; paths are fixed to the three policy documents in
        the data/policy-documents/ directory.
    output: >
      A combined structured dict or object where keys are document names and values
      are parsed sections and clauses, allowing the answering system to pinpoint
      exact citations.
    error_handling: >
      If any of the three required documents are missing, raise FileNotFoundError and
      halt initialization.

  - name: answer_question
    description: >
      Takes a user query, searches the indexed documents, and returns either a
      single-source factual answer with a citation, or the exact refusal template.
    input: >
      - query: string — The user's question.
    output: >
      A string containing the answer and citation (e.g. "[Source: policy_it_acceptable_use.txt, Section 2.3]")
      OR the exact refusal template if the answer is not found or requires cross-document blending.
    error_handling: >
      If the input query is empty or malformed, return the refusal template.
      If the query requires combining IT policy and HR policy to formulate an answer (e.g.
      personal phone usage for remote work), immediately fallback to the refusal template
      or a single-source answer without blending.
