# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Loads a policy document from a .txt file and returns its content as structured numbered sections.
    input: Path to the input .txt file (String).
    output: List of structured sections, each with a section number and text.
    error_handling: Logs errors and returns an empty structure if the file is missing or malformed.

  - name: summarize_policy
    description: Produces a compliant summary of policy sections with clause references, ensuring no meaning is lost.
    input: Structured policy sections from retrieve_policy.
    output: A summary string with clause citations (e.g., "[Clause 2.3]") and verbatim quotes where necessary.
    error_handling: Flags the summary for review if critical conditions are dropped or meaning is altered.

