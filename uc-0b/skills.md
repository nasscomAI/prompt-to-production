# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [retrieve_policy]
    description: [Loads a .txt policy file and parses its content into structured, explicitly numbered sections to ensure no clauses are omitted.]
    input: [String representing the file path to the policy document.]
    output: [Dictionary or structured list mapping each text section to its exact original clause number.]
    error_handling: [Halts execution if the file is unreadable or missing; if the document lacks clear numbering, returns the raw text with a warning flag instead of silently skipping unstructured paragraphs to prevent initial clause omission.]

  - name: [summarize_policy]
    description: [Synthesizes structured policy sections into a compliant summary that strictly preserves binding verbs, multi-condition obligations, and exact clause references.]
    input: [Dictionary or structured list containing the numbered policy sections mapped from the source document.]
    output: [String representing the concise policy summary with explicit references to all original numbered clauses.]
    error_handling: [If summarization risks softening obligations or dropping conditions from multi-condition rules (e.g., omitting one of two required approvers), quotes the specific clause verbatim and flags it; actively strips out any scope bleed or external generalizations not literally present in the input.]
