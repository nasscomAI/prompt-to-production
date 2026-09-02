# skills:

# 

# &#x20; - name: load\_dataset

# &#x20;   description: >

# &#x20;     Reads the ward budget CSV, validates the required columns, counts null

# &#x20;     actual\_spend values, and reports the affected rows and their notes.

# &#x20;   input: >

# &#x20;     Path to ward\_budget.csv.

# &#x20;   output: >

# &#x20;     Structured dataset containing period, ward, category, budgeted\_amount,

# &#x20;     actual\_spend, and notes, together with null-row information.

# &#x20;   error\_handling: >

# &#x20;     If the file cannot be read, required columns are missing, or the dataset

# &#x20;     is invalid, report the error and do not invent or substitute data.

# 

# &#x20; - name: compute\_growth

# &#x20;   description: >

# &#x20;     Computes growth for one explicitly selected ward and category using the

# &#x20;     explicitly requested growth type and returns a per-period table with

# &#x20;     the formula shown for every row.

# &#x20;   input: >

# &#x20;     Validated dataset, one ward, one category, and an explicit growth type

# &#x20;     such as MoM.

# &#x20;   output: >

# &#x20;     Per-period CSV-ready table containing period, ward, category,

# &#x20;     actual\_spend, formula, growth\_percent, and status or null reason.

# &#x20;   error\_handling: >

# &#x20;     Refuse if the growth type is missing or unsupported, the requested ward

# &#x20;     or category does not exist, or required actual\_spend values are null.

# &#x20;     Null rows must be flagged with their notes reason rather than calculated.

