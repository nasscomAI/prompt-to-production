skills:

&#x20; - name: retrieve\_documents

&#x20;   description: >

&#x20;     Loads all three policy files and indexes their content by document name

&#x20;     and numbered section.

&#x20;   input: >

&#x20;     Three UTF-8 .txt policy file paths.

&#x20;   output: >

&#x20;     Structured policy index mapping each filename to its numbered sections

&#x20;     and exact section text.

&#x20;   error\_handling: >

&#x20;     Rejects missing or unreadable policy files and identifies the affected

&#x20;     document.



&#x20; - name: answer\_question

&#x20;   description: >

&#x20;     Finds a supported answer in exactly one policy document and returns the

&#x20;     answer with its source filename and section citation, or returns the exact

&#x20;     refusal template.

&#x20;   input: >

&#x20;     A user question and the structured policy-document index.

&#x20;   output: >

&#x20;     A condition-preserving answer with one document and section citation, or

&#x20;     the exact required refusal response.

&#x20;   error\_handling: >

&#x20;     Refuses unsupported, ambiguous, or cross-document questions rather than

&#x20;     guessing or combining claims.



