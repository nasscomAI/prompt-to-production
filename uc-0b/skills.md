# notepad uc-0b\\skills.md

# ```

# 

# \*\*Ctrl+A → Delete\*\* and paste this:

# ```

# \# UC-0B — Policy Summary Skills

# 

# skills:

# 

# \- name: read\_policy

# &#x20; description: Reads and parses the HR leave policy document clause by clause.

# &#x20; input: policy\_hr\_leave.txt as plain text

# &#x20; output: List of numbered clauses with their full content

# &#x20; error\_handling: If file not found, raise error and stop. Never summarize from memory.

# 

# \- name: summarize\_clause

# &#x20; description: Summarizes a single clause without dropping any condition.

# &#x20; input: One numbered clause as plain text

# &#x20; output: Shortened version preserving all conditions, numbers, and approvers

# &#x20; error\_handling: If clause has multiple conditions, all must appear in output

# 

# \- name: preserve\_approval\_chain

# &#x20; description: Ensures multi-step approval processes are never reduced.

# &#x20; input: Clause containing approval steps

# &#x20; output: Summary with all approvers listed in correct order

# &#x20; error\_handling: If approver count in summary is less than source, rewrite

# 

# \- name: write\_summary

# &#x20; description: Writes the final summary file with all clauses represented.

# &#x20; input: List of summarized clauses

# &#x20; output: summary\_hr\_leave.txt with one section per clause

# &#x20; error\_handling: If any clause is missing, add it before writing output

