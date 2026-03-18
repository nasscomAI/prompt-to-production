# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content.
    input: File path (string).
    output: The full text of the policy document (string).
    error_handling: Raise an error if the file does not exist.

  - name: summarize_policy
    description: Takes the policy text and produces a compliant summary with clause references, ensuring no conditions are dropped.
    input: The structured policy text (string).
    output: A summary containing every numbered clause with preserved obligations (string).
    error_handling: If the input text is empty or invalid, return an error message indicating unsummarizable input.
