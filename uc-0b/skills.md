# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: Filepath string pointing to the policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: Structured data (e.g., JSON or object list) containing numbered sections and their raw text content.
    error_handling: System should halt and report if the file is unreadable or if parsing numbered structure fails.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured data array/list of numbered clauses output by the retrieve_policy skill.
    output: Markdown string summarizing the policy, preserving all specific multi-condition obligations.
    error_handling: If a clause cannot be concisely summarised without meaning loss, quote it verbatim and flag it instead of attempting an imperfect paraphase.
