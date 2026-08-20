# UC-X Policy Q&A Skills

skills:
  - name: retrieve_documents
    description: Load the policy documents and index their numbered sections for lookup.
    input: A repository root path containing the policy documents.
    output: A mapping of document names to a list of indexed section-number and text pairs.
    error_handling: Stop with a clear error if a required document is missing.

  - name: answer_question
    description: Search the indexed documents and return a single-source answer with a citation, or a fixed refusal message when the question is out of scope.
    input: A user question and the indexed policy documents.
    output: A plain-text answer or refusal template.
    error_handling: Refuse rather than guess when the source is missing or ambiguous.
