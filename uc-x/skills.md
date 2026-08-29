skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads all 3 policy files and indexes their content by document name and section number.

&#x20;   input: A list of file paths to the 3 policy documents.

&#x20;   output: A structured index (e.g. dict keyed by document name, each containing a dict of section number to section text).

&#x20;   error\_handling: If any document is missing or unreadable, raise a clear error listing which document failed to load.



&#x20; - name: answer\_question

&#x20;   description: Searches the indexed documents for content relevant to a question and returns either a single-source answer with citation, or the exact refusal template.

&#x20;   input: question (string), the document index from retrieve\_documents.

&#x20;   output: A dict or string containing either the answer text with a document+section citation, or the exact refusal template text.

&#x20;   error\_handling: If relevant content is found in more than one document and combining them would be required to answer, treat this as not answerable from a single source and use the refusal template rather than blending.

