# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:

name: retrieve_documents
description: Loads all specified policy files and indexes their content strictly by document name and section number.
input:
type: array
format: List of file paths to the policy text documents.
output:
type: object
format: A structured index mapping document names and explicit section numbers to their exact text content.
error_handling: Halts execution if a file is missing or if the text cannot be reliably parsed into explicit section numbers to prevent incomplete context.

name: answer_question
description: Searches the indexed documents to provide a definitive, single-source answer with explicit citations or outputs the strict refusal template.
input:
type: string
format: A user's question in natural language.
output:
type: string
format: A direct answer containing a single source document name and section number, or the exact refusal template text.
error_handling: Outputs the exact refusal template without any hedging phrases if the answer requires blending claims across multiple documents, if the condition dropping risk is high, or if the answer is not explicitly found.