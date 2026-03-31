skills:
  - name: retrieve_policy
    description: "Loads the .txt policy file and returns the content as structured, numbered sections."
    input: "String - Path to the policy .txt file."
    output: "A dictionary or list of structured sections containing clause numbers and their raw text."
    error_handling: "If the file is not found, or contains sections with missing clause numbers, log specific errors for those sections or flag the entire document as incomplete."

  - name: summarize_policy
    description: "Takes the structured sections from 'retrieve_policy' and produces a compliant summary that preserves all binding clauses and conditions."
    input: "Structured policy sections (from retrieve_policy)."
    output: "A string containing the compliant summary with all numbered clauses and multi-condition obligations fully preserved."
    error_handling: "Check for omitted clauses from the ground truth list (2.3 - 7.2) and ensure multi-condition approvals are not shortened to single-condition ones."
