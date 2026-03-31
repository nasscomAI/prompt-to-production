# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: [retrieve_documents]
    description: [Loads the HR, IT, and Finance policy files and precisely indexes their content by document name and section number to support accurate citation]
    input: [List of string file paths pointing to the three required policy text files.]
    output: [Structured dictionary or index mapping verbatim text chunks directly to their explicit source document names and designated section numbers.]
    error_handling: [Halts execution immediately if any of the three required files are missing or unreadable to prevent incomplete context retrieval.]

  - name: [answer_question]
    description: [Searches the indexed policy documents to confidently return a single-source cited answer or an exact refusal template if the answer is unavailable or ambiguous.]
    input: [A string representing the user's query and the structured index of the three policy documents.]
    output: [A string containing either the factual answer appended with a strict document/section citation, or the verbatim refusal template.]
    error_handling: [Systematically blocks cross-document blending by returning the exact refusal template if resolving the query demands combining claims from two distinct documents; explicitly rejects generating hedged hallucinatory prefixes like "while not explicitly covered" in favor of the mandated absolute refusal.]
