skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: Filepath to the .txt policy document (string)
    output: Content of the document parsed as structured numbered sections
    error_handling: Return an error message explicitly stating the file could not be read or parsed if the filepath is invalid

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections of the policy
    output: A compliant summary text preserving all obligations with their respective clause references (string)
    error_handling: Refuse to summarize and output an error if the input sections are empty or unparseable
