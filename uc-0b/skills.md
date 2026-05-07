


skills:

name: retrieve_policy
description: Loads a plain text policy file and returns its content organized into structured, numbered sections.
input:
type: string
format: File path to the .txt policy document.
output:
type: array
format: A structured list of objects mapping clause numbers to their exact text content.
error_handling: Halts execution and raises an error if the file cannot be read or if the text cannot be reliably parsed into numbered clauses, ensuring no clauses are omitted prior to summarization.

name: summarize_policy
description: Processes structured policy sections to generate a concise summary that strictly retains all clause references and binding multi-condition obligations.
input:
type: array
format: Structured list of objects containing clause numbers and their exact text content.
output:
type: string
format: Formatted text document containing the complete, compliant summary.
error_handling: Quotes the clause verbatim and explicitly flags it if summarization risks meaning loss, condition dropping, or obligation softening, and strictly rejects any inferred external context or standard practices to prevent scope bleed.