skills:
  - name: retrieve_policy
    description: Opens and reads a local .txt policy file, returning its entire text content.
    input: File path (string).
    output: Full text of the document as a string.
    error_handling: Raises FileNotFoundError if the file is missing or inaccessible.

  - name: summarize_policy
    description: Processes the policy text through an LLM using the strict enforcement rules in agents.md to produce a completely compliant summary.
    input: The full text of the policy document (string).
    output: A summarized text document (string) containing every required clause and condition.
    error_handling: Returns an error message if the LLM output is empty or if the API call fails.
