# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into a structured format of numbered sections.
    input: Absolute path to a .txt policy file.
    output: A structured map where keys are clause numbers (e.g., "2.3") and values are the corresponding text.
    error_handling: Return a FileNotFoundError if the path is invalid or a ParseError if the document lacks expected clause numbering.
    
  - name: summarize_policy
    description: Generates a high-fidelity summary of structured policy sections, preserving all binding conditions and clause references.
    input: A structured map of policy clauses and their content.
    output: A summary string where every clause is accounted for and complex obligations are fully detailed.
    error_handling: Refuse to summarize and return an error if a clause contains ambiguous conditions that cannot be simplified without meaning loss.
