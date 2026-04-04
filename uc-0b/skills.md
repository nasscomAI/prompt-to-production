# skills.md

skills:
  - name: retrieve_policy
    description: Recursively loads a local .txt policy document and parses its string contents into segregated, structured numbered sections to prevent clause loss.
    input: An absolute or relative file path pointing to the desired .txt policy file.
    output: A structured data object (e.g., list or dictionary) where each parsed numbered clause is an isolated string tied to its section identifier.
    error_handling: Halts execution and returns a formal error alert if the file path is invalid, unreadable, or structurally impossible to segregate by numbering.

  - name: summarize_policy
    description: Processes the structured policy sections to generate a verified summary ensuring zero capability softening and perfect conditional inheritance mapped to specific clause numbers.
    input: The structured data object yielded by retrieve_policy.
    output: A compiled, finalized string containing the compliant summary and explicit references to all integrated multi-condition approval chains.
    error_handling: Reverts to verbatim reproduction (prepended with "[FLAGGED VERBATIM]") whenever specific parsing logic fails to confidently abridge a highly complex legal clause without bleeding scope.
