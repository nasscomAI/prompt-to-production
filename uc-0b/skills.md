skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections to prevent omission of clauses.
    input: File path (string) of the .txt policy document.
    output: A structured text representation or JSON format containing all numbered clauses preserved intact.
    error_handling: If the file is missing or unreadable, returns an error stating "File not accessible or invalid format."

  - name: summarize_policy
    description: Takes the structured sections from the policy and produces a highly accurate and compliant summary that references and preserves all clauses and multi-condition obligations.
    input: Structured sections or raw text outputted by retrieve_policy.
    output: A comprehensive plain-text summary explicitly containing all numbered clauses and their respective rigorous conditions.
    error_handling: If any portion of the structured sections is ambiguous or resists summarization, quotes the source verbatim and flags it for review.
