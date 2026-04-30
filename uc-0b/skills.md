skills:
  - name: [retrieve_policy]
    description: [Reads a plain text HR leave policy file and parses its contents into structured, numbered sections for precise processing.]
    input: [type: string format: file path to the .txt policy document]
    output: [type: array format: structured list containing the clause number and the verbatim text of each section]
    error_handling: [If the input file is unreadable or lacks identifiable numbered clauses, it halts execution to prevent silent clause omission.]

  - name: [summarize_policy]
    description: [Processes structured policy clauses to generate a compliant summary that strictly preserves all original binding verbs, conditions, and explicit clause references.]
    input: [type: array format: structured list containing the clause number and verbatim text of each section]
    output: [type: string format: compliant text summary of the policy document with explicit clause references]
    error_handling: [If a clause cannot be summarized without risk of obligation softening or dropping multi-condition requirements, it quotes the clause verbatim and flags it, strictly avoiding any scope bleed additions.]