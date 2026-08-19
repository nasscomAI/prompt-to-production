skills:
  - name: retrieve_documents
    description: Loads policy documents (HR, IT, Finance) and indexes text by document filename and section numbers.
    input: Directory path to policy-documents.
    output: Indexed section store mapping document names and section IDs to text content.
    error_handling: Raise error if any of the mandatory 3 policy files are missing.

  - name: answer_question
    description: Searches the indexed policy documents for relevant sections and returns a cited single-source answer or the exact refusal template.
    input: User natural language query string.
    output: Single-source answer with document name and section citation, or exact refusal template.
    error_handling: If no single section covers the question or topic is unmentioned, return exact refusal template without hedging or blending.
