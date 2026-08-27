# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - retrieve_policy:
description: >
Loads the HR leave policy text file and converts it into structured, numbered sections for precise clause-level processing.
input: >
File path to .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt)
output: >
Structured representation of the document with clearly separated numbered clauses (e.g., 2.3, 2.4, etc.)
constraints:
- Must not alter, summarize, or interpret the content
- Must preserve exact wording and numbering from the source file
- Must return all sections present in the document without omission
error_handling:
- If file path is invalid or file cannot be found, return a clear error: "Input file not found"
- If file is empty or unreadable, return: "Input file is empty or unreadable"
- If expected clause numbering is missing or malformed, return: "Invalid or inconsistent clause structure"
- If partial content is loaded, flag: "Incomplete document retrieval"

summarize_policy:
description: >
Produces a clause-by-clause summary of the structured HR leave policy while preserving all obligations, conditions, and meanings exactly.
input: >
Structured numbered clauses from retrieve_policy
output: >
A compliant summary that includes all required clauses with preserved meaning, explicit conditions, and clause references
constraints:
- Must include every required clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2)
- Must retain all conditions in multi-condition clauses (e.g., both approvers in 5.2)
- Must preserve binding verbs and obligation strength exactly
- Must not introduce new information or assumptions
- If summarization risks meaning loss, must quote the clause verbatim and flag it
- Must avoid scope bleed or generic phrasing not present in the source document
error_handling:
- If input structure is missing required clauses, return: "Missing required clauses for summarization"
- If any clause cannot be summarized without meaning loss, quote verbatim and flag: "Verbatim required due to meaning preservation risk"
- If multi-condition clause is partially parsed, return: "Incomplete clause conditions detected"
- If output omits any required clause, return: "Summary incomplete: clause omission detected"
- If conflicting interpretations arise, return: "Ambiguous clause interpretation — requires review"