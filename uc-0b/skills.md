# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path to the .txt policy file.
    output: A dictionary or list mapping section numbers to their text content.
    error_handling: Return an error if the file cannot be read or parsed properly.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant, accurate summary emphasizing required clauses without losing multi-condition obligations.
    input: Structured sections retrieved from the policy document.
    output: A standardized text string summarizing all key clauses accurately.
    error_handling: Flag and quote any clause verbatim if it cannot be summarized without altering its meaning.
