skills:
  - name: retrieve_policy
    description: Opens and reads the policy .txt file, returning its full textual content.
    input: A string representing the absolute or relative file path to the policy document.
    output: A string containing the full text of the policy document.
    error_handling: If the file is not found or cannot be read, raise a FileNotFoundError.

  - name: summarize_policy
    description: Analyzes the retrieved policy text and generates a compliant summary preserving the 10 target clauses exactly without condition drops.
    example_invocation:
      call: `summarize_policy({"policy_text": "5.2 LWP requires approval from the Department Head and the HR Director. Manager approval alone is not sufficient."})`
      returns: `"[Clause 5.2] LWP requires approval from the Department Head and the HR Director."`
    input: A string containing the extracted policy text.
    output: A string containing the generated summary formatted with clause references.
    error_handling: Return original text with an error warning if the summarization process encounters an extraction failure or ambiguity.
