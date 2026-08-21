skills:
  - name: retrieve_policy
    description: Loads a technical HR policy document and parses it into a structured dictionary of numbered sections to ensure precise referencing.
    input: Absolute path to the policy text file (.txt).
    output: A structured dictionary mapping clause numbers (e.g., "5.2") to their exact raw text content.
    error_handling: Refuses to proceed if the file is missing, inaccessible, or if the content does not contain discernable clause numbering.

  - name: summarize_policy
    description: Generates a verifiable summary of structured policy sections while preserving all binding obligations and multi-condition requirements.
    input: Structured policy dictionary and a "Clause Inventory" specifying core obligations to be preserved.
    output: A point-by-point summary where each point references the source clause and maintains exact legal/binding conditions.
    error_handling: Quotes text verbatim and flags for manual review if a clause cannot be compressed without meaning loss; refuses to summarize sections with internal contradictions.
