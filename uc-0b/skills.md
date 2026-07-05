skills:
  - name: retrieve_policy
    description: Loads a CMC policy text file and parses it into structured numbered sections.
    input:
      type: string
      format: Absolute path to the policy text file (e.g., path/to/policy_hr_leave.txt)
    output:
      type: dict
      format: A dictionary mapping clause numbers (e.g., "2.3", "5.2") to their exact raw text sentences.
    error_handling: Raises a FileNotFoundError if the file doesn't exist, or a ValueError if the file is empty or does not contain recognizable CMC leave policy reference codes.

  - name: summarize_policy
    description: Takes the structured sections of the leave policy and generates a compliant, high-fidelity summary adhering to enforcement rules.
    input:
      type: dict
      format: A dictionary of structured clauses/sections from retrieve_policy.
    output:
      type: string
      format: A formatted text summary containing the summarized/verbatim obligations with explicit clause references.
    error_handling: If any of the mandatory clauses are missing from the input, or if there is ambiguity in a clause's conditions that might cause meaning loss, quotes the clause verbatim, flags it, and appends a warning block.

