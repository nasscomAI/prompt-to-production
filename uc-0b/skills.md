# \# Skills

# 

# \## retrieve\_policy

# Loads the HR leave policy text file.

# 

# Input: policy text file (.txt)

# 

# Output: structured sections of the policy with numbered clauses.

# 

# 

# \## summarize\_policy

# Creates a summary of the policy while preserving all obligations.

# 

# Rules:

# \- Every numbered clause must appear in the summary.

# \- Multi-condition obligations must preserve ALL conditions.

# \- Never add information that is not in the source policy.

# \- If summarizing would lose meaning, quote the clause verbatim.

# 

# Output: structured policy summary referencing clause numbers.

