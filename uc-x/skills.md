# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy text files and indexes their content by document filename and section number, returning a structured map ready for lookup.
    input: A list of file paths (strings) pointing to the three policy .txt files.
    output: A nested dict indexed as {filename: {section_number: section_text}}, e.g. {"policy_hr_leave.txt": {"2.6": "Employees may carry forward..."}}.
    error_handling: Raises an error and halts if any of the three files cannot be found or read; reports which file is missing so the user can fix the path before querying.

  - name: answer_question
    description: Searches the indexed document map for a single-source answer to a question, returns the answer with exact citation, or the mandatory refusal template if not found.
    input: A question string and the document index dict produced by retrieve_documents.
    output: A formatted string containing either (a) the factual answer with citation "Source: {filename} § {section}" or (b) the exact refusal template verbatim with no additions.
    error_handling: If matches are found in more than one document for the same question, outputs a single-source answer from the most specific match only — never blends across documents; if specificity is truly ambiguous, outputs the refusal template.
