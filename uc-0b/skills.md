# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns content as structured numbered sections
    input: path — file path to the policy .txt file
    output: structured sections with clause number, text, and binding verb
    error_handling: If file not found or malformed, returns empty structured list and logs error

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references preserving all conditions
    input: structured sections from retrieve_policy
    output: summary text with all 10 clauses present, multi-condition obligations preserve ALL conditions, verbatim quotes for meaning-loss cases
    error_handling: If any clause is missing conditions, flag it; if clause cannot be summarised without meaning loss, quote it verbatim and flag it