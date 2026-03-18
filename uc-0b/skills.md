# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content organized as structured numbered sections.
    input: File path of the policy document (e.g., policy_hr_leave.txt).
    output: A structured object or list of strings where each element represents a numbered section with its corresponding text.
    error_handling: Return an error if the file cannot be read or if no numbered sections can be identified.

  - name: summarize_policy
    description: Takes structured sections of a policy and produces a compliant summary that strictly maintains clauses and conditions.
    input: Structured numbered sections from retrieve_policy.
    output: A text summary containing clause references without omitted conditions or softened obligations.
    error_handling: Refuse to summarize if the input text contains ambiguous multipart conditions that cannot be mapped.
