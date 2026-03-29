skills:
  - name: retrieve_documents
    description: Loads all specified policy files (HR, IT, Finance) and indexes their contents accurately by document name and section number.
    input: List of file paths to the policy text files.
    output: A structured index mapping section numbers to text content for each distinct document name.
    error_handling: If a file cannot be read, immediately reports the failure without processing partial data.

  - name: answer_question
    description: Searches the indexed policy documents for a specific query and returns a single-source factual answer with citation.
    input: The user's query string and the loaded index of policy documents.
    output: A single string containing the factual answer and strict citation (document name + section), OR the exact refusal template.
    error_handling: If the query requires information from multiple documents or is ambiguous, it returns the exact refusal template to prevent blended hallucination.
