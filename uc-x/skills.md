# notepad uc-x\\skills.md

# ```

# 

# When Notepad opens, \*\*Ctrl+A → Delete\*\* and paste this:

# ```

# \# UC-X — Ask My Documents Skills

# 

# skills:

# 

# \- name: identify\_source\_document

# &#x20; description: Determines which single document can answer the question.

# &#x20; input: question as plain text

# &#x20; output: exactly one filename from the 3 policy documents

# &#x20; error\_handling: If no document matches, return CANNOT ANSWER

# 

# \- name: extract\_answer

# &#x20; description: Extracts the precise answer from the identified document only.

# &#x20; input: question and source document content

# &#x20; output: answer text with filename citation

# &#x20; error\_handling: If answer not found in identified document, return CANNOT ANSWER

# 

# \- name: enforce\_single\_source

# &#x20; description: Ensures answer never blends content from multiple documents.

# &#x20; input: draft answer and list of documents referenced

# &#x20; output: validated answer citing exactly one document

# &#x20; error\_handling: If multiple documents referenced, reject and rewrite

# 

# \- name: handle\_refusal

# &#x20; description: Returns a clear refusal when question cannot be answered.

# &#x20; input: question that has no match in any document

# &#x20; output: "CANNOT ANSWER: This information is not found in the provided documents"

# &#x20; error\_handling: Never guess — always refuse if not found

