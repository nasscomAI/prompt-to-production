skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns it as structured, numbered sections.
    input: 
      - file_path (string): The path to the policy .txt file.
    output: 
      - structured_sections (list of dicts): The numbered sections and their raw text content.
    error_handling: "If the file is unreadable, fail cleanly."

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input:
      - structured_sections (list of dicts): The output from retrieve_policy.
    output: 
      - summary (string): The final summarized text adhering to the policy_summarizer rules.
    error_handling: "Must preserve clause numbers in the output. Provide verbatim quotes if summary compresses meaning too much."
