# skills:

# &#x20; - name: retrieve\_documents

# &#x20;   description: Loads the three policy documents and indexes their content by document name and section number.

# &#x20;   input: File paths for the three policy documents.

# &#x20;   output: Indexed policy documents with document names, section numbers, and section content.

# &#x20;   error\_handling: If a required file is missing or cannot be read, report the error and do not answer using incomplete documents.

# 

# &#x20; - name: answer\_question

# &#x20;   description: Searches the indexed policy documents and returns a supported answer from one document only.

# &#x20;   input: A user question as a string and the indexed policy documents.

# &#x20;   output: A single-source answer with the source document name and section number, or the exact refusal template.

# &#x20;   error\_handling: If the question is invalid, ambiguous, unsupported, or requires combining claims from multiple documents, return the refusal template instead of guessing.

