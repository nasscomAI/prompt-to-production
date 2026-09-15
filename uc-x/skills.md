# skills:

# &#x20; - name: retrieve\_documents

# &#x20;   description: Loads all 3 policy files and indexes them by document name and section number, handling clauses that wrap across multiple lines.

# &#x20;   input: Directory path containing the 3 policy .txt files.

# &#x20;   output: A dict of {document\_filename: {section\_number: clause\_text}}.

# &#x20;   error\_handling: If a required document file is missing, raise a clear error naming the missing file rather than silently proceeding with 2 documents.

# 

# &#x20; - name: answer\_question

# &#x20;   description: Searches indexed documents using weighted keyword matching, returning a single-source answer with citation or the exact refusal template if no document scores highly enough.

# &#x20;   input: A free-text question string, the indexed documents, and a precomputed word-rarity weighting table.

# &#x20;   output: Either a formatted answer citing one document and one or more section numbers from that same document, or the exact refusal template string.

# &#x20;   error\_handling: If the question contains no meaningful keywords, or no document scores above threshold, return the refusal template rather than guessing.

