# skills.md

skills:
  - name: retrieve_policy
    description: Loads the raw HR leave policy .txt file and processes its content into structured, numbered sections / clauses.
    input: Filepath to the raw policy document (e.g., policy_hr_leave.txt).
    output: A structured object (like a dictionary or parsed text) clearly demarcating all section headers and numbered clauses.
    error_handling: Refuses to process if the file is missing, empty, or unreadable, halting execution with an error statement.

  - name: summarize_policy
    description: Receives the structured policy clauses and produces a strict, compliant summary retaining exact meanings, multi-condition obligations, and clause references.
    input: Structured clause data from 'retrieve_policy'.
    output: A single string or formatted text block summarizing the policy, explicitly maintaining mandatory verbs and dual-approval requirements.
    error_handling: If a clause cannot be compressed without dropping conditions or altering its meaning, it quotes the clause verbatim and flags it in the summary rather than guessing.
