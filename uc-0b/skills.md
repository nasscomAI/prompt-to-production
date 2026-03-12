# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections for accurate parsing.
    input: "file_path: string (The path to the policy .txt file)"
    output: "List of structured sections and their clauses (e.g., [{'section_number': '1.0', 'clauses': [...] }])"
    error_handling: "If the file is not found or unreadable, return an empty list and log a file parsing error."

  - name: summarize_policy
    description: Takes structured sections and produces a compliant, loss-less summary with explicit clause references.
    input: "sections: List of structured sections from retrieve_policy"
    output: "summary: string (A fully compliant text summary covering every clause)"
    error_handling: "If input is empty, return an error message indicating no policy sections were provided."
