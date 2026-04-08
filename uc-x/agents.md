# agents.md

# INSTRUCTIONS: Generate a draft using your RICE prompt, then manually refine this file.

# Delete these comments before committing.

agents:

&nbsp; - name: qa\_agent

&nbsp;   role: Answers user questions from documents.

&nbsp;   skills\_used: \[search\_documents, extract\_answer]

&nbsp;   decision\_logic: Finds relevant documents and extracts answers.

&nbsp;   error\_handling: Returns "answer not found" if no match.



&nbsp; - name: index\_agent

&nbsp;   role: Builds a searchable index of documents.

&nbsp;   skills\_used: \[search\_documents]

&nbsp;   decision\_logic: Organizes documents for faster search.

&nbsp;   error\_handling: Skips documents that cannot be indexed.



