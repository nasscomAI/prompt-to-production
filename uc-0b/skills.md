# skills:

# 

# \- name: retrieve\_policy

# &#x20; description: Read the HR leave policy and preserve all numbered clauses, conditions, exceptions, obligations, approvals, and time limits.

# &#x20; input: Path to the policy\_hr\_leave.txt file.

# &#x20; output: Structured policy content containing clause numbers and source text.

# &#x20; error\_handling: Reject missing or unreadable files; never invent missing policy content.

# 

# \- name: summarize\_policy

# &#x20; description: Create a concise summary while preserving every required clause, condition, exception, obligation, approval requirement, and time limit.

# &#x20; input: Structured numbered policy clauses from the source document.

# &#x20; output: Clause-referenced summary containing all required policy requirements.

# &#x20; error\_handling: If a clause cannot be safely summarized without changing its meaning, quote it verbatim and flag it for review.

