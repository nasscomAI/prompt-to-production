skills:
  - name: [retrieve_policy]
    description: [Loads a .txt policy file and returns its content mapped into structured, numbered sections.]
    input: [type: string format: File path to the source .txt document]
    output: [type: array format: List of objects containing clause numbers and verbatim text]
    error_handling: [Returns an error if the file cannot be found, is not readable, or if the content cannot be parsed into numbered sections.]

  - name: [summarize_policy]
    description: [ Processes structured policy sections to produce a compliant summary with explicit clause references while strictly preserving all original conditions and binding obligations.]
    input: [type: array format: List of objects containing clause numbers and verbatim text]
    output: [type: string format: Text summary containing all numbered clauses and their preserved obligations]
    error_handling: [Quotes the original clause verbatim and flags it in the summary if the input is ambiguous or if summarizing it would lead to clause omission, condition dropping, obligation softening, or scope bleed.]
