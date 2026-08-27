# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: "retrieve_policy"
    description: "Loads a policy document from a text file and parses it into numbered sections and clauses."
    input: "Path to the .txt policy file."
    output: "A dictionary or list of structured segments, indexed by section/clause numbers."
    error_handling: "Return an error if the file cannot be read or if section numbers cannot be extracted."

  - name: "summarize_policy"
    description: "Summarizes structured policy sections while strictly enforcing the preservation of mandatory clauses and conditions."
    input: "Structured policy segments and a list of mandatory ground-truth clauses."
    output: "A concatenated summary where each mandatory clause is preserved with its full obligations and conditions."
    error_handling: "Include a 'MISSING_CLAUSE' warning in the output if a mandatory clause was not found in the input."
