skills:
  - name: "retrieve_policy"
    description: "Loads a .txt policy file and returns its content as structured numbered sections."
    input: "Type: string, Format: file path to a .txt document"
    output: "Type: structured array, Format: list of policy clauses mapped by their section numbers"
    error_handling: "Halt execution and throw an error if the input file does not exist, is invalid, or if the content cannot be successfully parsed into distinct numbered sections."

  - name: "summarize_policy"
    description: "Takes structured sections and produces a compliant summary with explicit clause references."
    input: "Type: structured array, Format: list of policy clauses mapped by their section numbers"
    output: "Type: string, Format: summarized text document containing explicit clause references"
    error_handling: "If summarization detects clause omission, drops multiple conditions (e.g., missing one of multiple approvers), softens obligations, introduces scope bleed (e.g., 'as is standard practice', 'typically in government organisations'), or if a clause cannot be summarized without meaning loss, quote the clause verbatim and flag the failure."
