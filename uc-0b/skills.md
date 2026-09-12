# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path to the policy document (string)
    output: A list of structured sections, each with a clause number and content (list of dicts).
    error_handling: Raises an error if the file is not found or unreadable.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: A list of structured policy sections (list of dicts).
    output: A string containing the summarized policy document.
    error_handling: Returns an empty string if input sections are empty.
