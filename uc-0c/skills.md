# \# skills.md — UC-0C Growth Analysis

# 

# skills:

# &#x20; - name: load\_dataset

# &#x20;   description: Reads the ward budget CSV, validates required columns, and reports null actual\_spend rows.

# &#x20;   input: A CSV file containing period, ward, category, budgeted\_amount, actual\_spend, and notes.

# &#x20;   output: Validated dataset with null rows and their reasons identified.

# &#x20;   error\_handling: If required columns are missing or the file cannot be read, stop and report the error.

# 

# &#x20; - name: compute\_growth

# &#x20;   description: Calculates growth for one requested ward, category, and growth type with the formula shown.

# &#x20;   input: Validated dataset plus ward, category, and growth\_type.

# &#x20;   output: Per-period growth table with actual\_spend, formula, result, and null flags where applicable.

# &#x20;   error\_handling: Refuse missing growth\_type, invalid ward/category, or calculations involving missing actual\_spend instead of guessing.

