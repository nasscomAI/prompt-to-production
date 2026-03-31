skills:
  - name: retrieve_documents
    description: loads all 3 policy files, indexes by document name and section number
    input: File paths to the three policy document texts.
    output: An indexed collection of policy text chunks mapped by document name and section number.
    error_handling: Return a clear error if the files cannot be found or read.

  - name: answer_question
    description: searches indexed documents, returns single-source answer + citation OR refusal template
    input: The user's question string and the retrieved indexed documents.
    output: A single-source answer string with citation (document name + section number), OR the exact refusal template string.
    error_handling: Return the exact refusal template if the answer is not firmly supported or would require blending documents.
