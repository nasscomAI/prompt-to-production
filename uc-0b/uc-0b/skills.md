# skills.md

skills:
  - name: retrieve_policy
    description: Reads the raw text file of the policy document and returns it as structured, line-by-line sections to facilitate accurate extraction.
    input: A string representing the file path to the text document.
    output: A list of strings, where each string represents a line or block of text from the policy.
    error_handling: Raise an exception if the file cannot be found or read, clearly stating the path attempted.

  - name: summarize_policy
    description: Processes the structured policy sections to extract all numbered clauses verbatim, prepending each with a [VERBATIM] flag to guarantee zero meaning loss.
    input: A list of text strings from retrieve_policy.
    output: A single string containing the compiled summary of verbatim clauses, ready to be written to a file.
    error_handling: Must not drop any numbered clauses. If a section is malformed, still attempt to extract any numbers matching the clause pattern.
