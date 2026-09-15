# skills:

# &#x20; - name: load\_dataset

# &#x20;   description: Reads the ward budget CSV, validates required columns are present, and reports the count and details of null actual\_spend rows before returning parsed data.

# &#x20;   input: File path to ward\_budget.csv.

# &#x20;   output: A list of row dicts with actual\_spend parsed as float or None, plus a printed report of which rows are null and why.

# &#x20;   error\_handling: If required columns are missing, raise a clear error naming which columns are absent rather than proceeding with partial data.

# 

# &#x20; - name: compute\_growth

# &#x20;   description: Filters data to a single ward and category, then computes per-period MoM or YoY growth, showing the formula used for every row.

# &#x20;   input: Parsed dataset rows, a ward name, a category name, and a growth\_type (MoM or YoY).

# &#x20;   output: A list of per-period result dicts with growth\_pct, formula, and a flag field for periods that could not be computed.

# &#x20;   error\_handling: If the ward/category combination has no matching rows, raise a clear error. If a period's calculation depends on a null value, flag it as NULL\_NOT\_COMPUTED rather than skip or estimate it.

