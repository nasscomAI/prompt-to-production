# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and transforms it into a structured format of numbered sections for precise analysis.
    input: String representing the file path to the policy .txt file.
    output: A structured object or collection containing clauses and their associated text content.
    error_handling: Raises an error and stops processing if the file cannot be found, is unreadable, or does not follow a numbered clause structure.

  - name: summarize_policy
    description: Generates a summary of the structured policy content while strictly adhering to the clause inventory and enforcement rules.
    input: Structured policy sections (object) and a list of mandatory clauses to verify.
    output: A summarized text document with explicit clause references and preserved multi-condition obligations.
    error_handling: Flags a deficiency in the output if any mandatory clause is missing or if a multi-condition obligation has been simplified or dropped.
