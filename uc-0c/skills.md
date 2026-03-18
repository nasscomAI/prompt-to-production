# \# UC-0C — Budget Analysis Skills

# 

# skills:

# 

# \- name: read\_budget\_data

# &#x20; description: Reads ward budget CSV and validates all required columns exist.

# &#x20; input: ward\_budget.csv with columns ward, category, previous\_year, current\_year

# &#x20; output: List of rows with ward, category, previous and current budget values

# &#x20; error\_handling: If columns missing, print error and stop. Never assume column names.

# 

# \- name: compute\_growth

# &#x20; description: Computes percentage growth per ward per category.

# &#x20; input: One row with ward, category, previous\_year, current\_year values

# &#x20; output: growth\_pct as float rounded to 2 decimal places

# &#x20; error\_handling: If previous\_year is zero or null, return NULL not 0

# 

# \- name: flag\_nulls

# &#x20; description: Detects and flags missing or null values before computation.

# &#x20; input: Full dataset as list of rows

# &#x20; output: Printed warning for every null found, with ward and category identified

# &#x20; error\_handling: Never skip a null silently — always flag it

# 

# \- name: write\_growth\_output

# &#x20; description: Writes per-ward per-category growth results to CSV.

# &#x20; input: List of rows with ward, category, growth\_pct

# &#x20; output: growth\_output.csv with one row per ward per category

# &#x20; error\_handling: If any ward or category from input is missing in output, raise error

