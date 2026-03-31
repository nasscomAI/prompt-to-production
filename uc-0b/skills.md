skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns content parsed into structured numbered sections for precise clause tracking.
    input: File path (string) to the policy document (e.g., policy_hr_leave.txt).
    output: A dictionary or structured object containing numbered sections and their corresponding text.
    error_handling: Returns an error if the file is not found, unreadable, or lacks a numbered structure.

  - name: summarize_policy
    description: Processes structured policy sections into a compliant summary that preserves all binding obligations and clause references.
    input: Structured policy sections (object) and a target clause inventory (as defined in README.md).
    output: A summary document (text) that successfully represents all 10 core clauses (2.3 through 7.2) with preserved conditions.
    error_handling: If a clause's complexity prevents summarization without meaning loss, it is quoted verbatim and flagged as "Meaning Loss Risk."
