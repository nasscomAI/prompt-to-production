retrieve_policy:
  name: retrieve_policy
  [cite_start]description: Loads the .txt policy file and returns the content as structured numbered sections to ensure no clause is missed. [cite: 377, 385]
  input:
    type: string
    [cite_start]format: File path to the policy document (e.g., ../data/policy-documents/policy_hr_leave.txt). [cite: 386]
  output:
    type: object
    [cite_start]format: Structured dictionary or list containing numbered sections and their corresponding text. [cite: 387]
  error_handling:
    [cite_start]on_invalid_input: Return an error if the file path is incorrect or the file is unreadable. [cite: 388]
    [cite_start]on_missing_clauses: Flag an error if the expected 10 core clauses (2.3 to 7.2) are not detected in the source. [cite: 388]

summarize_policy:
  name: summarize_policy
  [cite_start]description: Takes structured sections and produces a compliant summary that preserves all conditions and clause references. [cite: 377, 385]
  input:
    type: object
    [cite_start]format: Structured policy sections provided by the retrieve_policy skill. [cite: 386]
  output:
    type: string
    [cite_start]format: A text summary containing all numbered clauses and full multi-condition obligations. [cite: 387]
  error_handling:
    [cite_start]on_meaning_loss: If a clause cannot be shortened without losing strictness, the skill must quote it verbatim and add a warning flag. [cite: 388]
    [cite_start]on_condition_drop: If the AI attempt results in dropping a condition (like an approver in Clause 5.2), it must retry or refuse the summary. [cite: 388]