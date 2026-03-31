# skills.md — UC-0B Policy Summary Auditor

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and restructure it into numbered sections for easy retrieval and auditing.
    input: File path to the policy .txt file.
    output: A dictionary where keys are section/clause numbers and values are the corresponding clause text.
    error_handling: "Return an error if the file is not found or is in an unsupported format."

  - name: summarize_policy
    description: Transform structured sections into a condensed summary while strictly adhering to the preservation rules in agents.md.
    input: Dictionary of numbered sections.
    output: A formatted string containing the summary with clause references and any verbatim quotations or flags.
    error_handling: "Flag sections that are too complex to summarize without risking loss of meaning for manual review."
