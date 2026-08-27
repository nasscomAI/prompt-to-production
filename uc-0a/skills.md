# skills:

# 

# \- name: classify\_complaint

# &#x20; description: Classify one citizen complaint into an allowed category and priority with a justified reason and review flag.

# &#x20; input: A single complaint row as a dictionary containing the complaint description and complaint\_id.

# &#x20; output: A dictionary containing complaint\_id, category, priority, reason, and flag.

# &#x20; error\_handling: Handle missing or invalid complaint data safely; use Other with NEEDS\_REVIEW when the category is genuinely ambiguous and never invent unsupported categories.

# 

# \- name: batch\_classify

# &#x20; description: Read a complaint CSV, classify every row using classify\_complaint, and write the classification results to an output CSV.

# &#x20; input: Input CSV file path and output CSV file path.

# &#x20; output: CSV containing complaint\_id, category, priority, reason, and flag for each input row.

# &#x20; error\_handling: Handle null values and bad rows without crashing; continue processing remaining rows and produce the output CSV even when individual rows fail.

