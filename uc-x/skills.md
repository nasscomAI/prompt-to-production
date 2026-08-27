# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files iteratively, parsing and indexing them by document name and distinct section numbering limiters.
    input: 
      - None (or directory paths containing the specific policy docs).
    output: 
      - Data structure indexing every clause to exact document_name + section_number maps.
    error_handling: 
      Throws an immediate startup error if any of the three explicit policy files is missing or malformed to prevent partial context gaps.

  - name: answer_question
    description: Searches the mapped sections for an exact non-ambiguous single-source match, returning the answer string natively appended with a strict citation format.
    input: 
      - user_query (str): The natural language query to check against policies.
      - document_index (dict): The mapped data structure from retrieve_documents.
    output: 
      - formatted_answer (str): A direct answer bounded by constraints + citation.
    error_handling: 
      If the system detects cross-document blending, partial overlaps with opposing intent, or has missing scope, it immediately returns the universal REFUSAL template verbatim without any added conversational filler.
