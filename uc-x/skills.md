# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: search_documents
    description: Locate the policy document most relevant to the user's question.
    input: User question and directory containing policy documents.
    output: The name and content of the most relevant policy document.
    error_handling: If no relevant document is found, return None.

  - name: extract_answer
    description: Extract the relevant sentence or rule from the selected document that answers the question.
    input: Selected document text and user question.
    output: A short answer along with the document name as the source.
    error_handling: If the answer cannot be located, return INFORMATION_NOT_FOUND.