skills:
  - name: retrieve_documents
    description: Parses input .txt files and clusters contents by document name and explicit section milestones.
    input: List of file path parameters.
    output: A dictionary mapping document origins to structured section strings.
    error_handling: System halts execution if any of the three foundational files are missing.

  - name: answer_question
    description: Validates user query text against indexed segments to output single-source claims with clear citations.
    input: Question string along with parsed context data blocks.
    output: An unblended response with clear citations, or the exact mandated refusal block.
    error_handling: Triggers the exact verification refusal template if text contains zero matching content.
