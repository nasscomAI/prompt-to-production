# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Reads a text policy document and extracts its content into structured numbered sections.
    input: File path to the .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A structured object (list or dictionary) mapping each numbered clause to its text.
    error_handling: If the file cannot be read or lacks clear numbered sections, return an error or parse the entire document as a single unnumbered section.

  - name: summarize_policy
    description: Processes structured policy sections to produce a concise summary that preserves all core obligations, multi-condition requirements, and binding verbs.
    input: The structured numbered sections outputted by the retrieve_policy skill.
    output: A text summary string that includes explicit clause references and strictly adheres to the source meaning.
    error_handling: If a clause cannot be summarised without meaning loss or softening its obligation, quote the clause verbatim and append a "[NEEDS_REVIEW]" flag to it.
