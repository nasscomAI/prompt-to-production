# skills.md

skills:
  - name: retrieve_documents
    description: Loads a list of policy files and indexes their content by document name and section number.
    input: List of file paths to policy documents.
    output: An indexed knowledge base mapping section numbers and document names to text.
    error_handling: Alert if any document in the list fails to load.

  - name: answer_question
    description: Searches indexed documents to answer employee questions and returns the answer with a citation, or a refusal.
    input: An employee's question string and the indexed document knowledge base.
    output: A single-source answer with document name and section citation, or the exact refusal template.
    error_handling: If no exact answer is found without blending or hedging, output the strict refusal template.
