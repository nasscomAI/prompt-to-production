# \# UC-0C Agent Instructions

# 

# \## Ground truth

# 

# The budget dataset must be analysed at the requested ward + category level.

# 

# \## Enforcement rules

# 

# 1\. Never aggregate across wards or categories unless explicitly instructed.

# &#x20;  If an all-ward or all-category aggregation is requested, refuse it.

# 

# 2\. Flag every null actual\_spend row before computing growth.

# &#x20;  Report the null reason from the notes column.

# 

# 3\. Show the formula used in every output row alongside the result.

# 

# 4\. If --growth-type is not specified, refuse and ask the user to specify it.

# &#x20;  Never guess between MoM, YoY, or another growth calculation.

# 

# 5\. Do not silently replace, ignore, or invent missing values.

# 

# 6\. Preserve the requested aggregation level: output must remain a

# &#x20;  per-period table for the specified ward and category.

