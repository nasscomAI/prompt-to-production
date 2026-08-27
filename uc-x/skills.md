# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: file_paths (list of str) - Paths to the policy .txt files.
    output: index (dict) - A structured index of the policies.
    error_handling: Raise an error if a file is missing or cannot be parsed.

  - name: answer_question
    description: Searches the indexed documents, applies strict rules to prevent blending, and returns a single-source answer with a citation, OR the exact refusal template.
    input: index (dict), question (str)
    output: answer (str) - The compliant answer or refusal.
    error_handling: If a question spans multiple conflicting documents, refuse to answer.
