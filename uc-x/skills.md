skills:
  - name: search_documents
    description: Searches policy documents for relevant content.
    input: User question.
    output: Relevant document excerpts.
    error_handling: Return NEEDS_REVIEW if no match found.

  - name: generate_answer
    description: Generates answer from retrieved document text.
    input: Question and document excerpts.
    output: Short factual answer.
    error_handling: Return Information not found if no answer exists.
