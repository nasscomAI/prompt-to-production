# skills.md

# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.

# Delete these comments before committing.

skills:

&nbsp; - name: search\_documents

&nbsp;   description: Finds relevant documents based on a user query.

&nbsp;   input: Query text (string)

&nbsp;   output: List of document references

&nbsp;   error\_handling: Returns empty list if no match found.



&nbsp; - name: extract\_answer

&nbsp;   description: Pulls the answer from the most relevant document.

&nbsp;   input: Document text (string)

&nbsp;   output: Answer (string)

&nbsp;   error\_handling: Returns "answer not found" if extraction fails.



