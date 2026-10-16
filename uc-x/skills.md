skills:
name: retrieve_documents
description >
   - Loads the three policy documents and validates that they exist, are readable, and contain policy text.
input >
   - A list of file paths to the policy documents.
output >
   -  A dictionary keyed by document filename containing the full text of each loaded document.
error_handling >
   -  Raise a file-not-found or empty-file error before any answer is produced; never continue with missing or blank inputs.

name: answer_question
description >
   -  Matches a user question against the relevant policy section and returns a single-source answer or the required refusal template.
input >
   - A natural-language question string and the loaded document dictionary.
output >
   - A plain-language response with the document name and section number when supported, or the exact refusal template when the answer is unsupported or requires cross-document blending.
error_handling >
   -  Refuse unsupported, ambiguous, or cross-document questions instead of guessing; never use hedging language or combine sources.
