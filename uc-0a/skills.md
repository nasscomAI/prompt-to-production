# \# Skills — UC-0A Complaint Classifier

# 

# skills:

# 

# &#x20; - name: classify\_complaint

# &#x20;   description: Classifies one citizen complaint using the deterministic taxonomy and priority rules.

# &#x20;   input: One complaint record as a Python dictionary containing a description field.

# &#x20;   output: A dictionary containing exactly category, priority, reason, and flag.

# &#x20;   error\_handling: If the description is missing or no category can be determined, use Other and NEEDS\_REVIEW; never invent a category or fact.

# 

# &#x20; - name: batch\_classify

# &#x20;   description: Classifies every complaint in a CSV file and writes the validated results.

# &#x20;   input: Input CSV path containing complaint records with a description column, and an output CSV path.

# &#x20;   output: CSV containing all original columns unchanged plus category, priority, reason, and flag.

# &#x20;   error\_handling: Process every row without crashing on an individual bad row; preserve the row and use Other with NEEDS\_REVIEW when classification cannot be determined.

