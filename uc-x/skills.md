skills:
  - name: retrieve_documents
    description: Loads all policy text files, parses them into indexed sections, and returns structured search targets.
    input: Directory path or list of policy file paths
    output: Index of sections mapped to policy document names and clause references
    error_handling: Handles missing documents with informative error messages.

  - name: answer_question
    description: Queries the indexed policy documents for a given question and returns either a cited single-source answer or the standardized refusal.
    input: Question string (str), indexed documents (dict)
    output: Formatted answer string with citations or exact refusal template
    error_handling: Uses exact refusal template whenever no direct policy match is found.
