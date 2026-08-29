skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the ward budget CSV, validates its columns, and reports the null count and which specific rows are null before returning data.

&#x20;   input: file\_path (path to ward\_budget.csv).

&#x20;   output: The full dataset (e.g. list of dicts), plus a separate list of null rows with their period, ward, category, and notes reason.

&#x20;   error\_handling: If required columns are missing or the file can't be read, raise a clear error rather than returning partial data silently.



&#x20; - name: compute\_growth

&#x20;   description: Filters the dataset to one ward and category, then computes period-over-period growth (MoM or YoY) with the formula shown for each row.

&#x20;   input: dataset (from load\_dataset), ward, category, growth\_type (MoM or YoY).

&#x20;   output: A per-period table with period, actual\_spend, growth value, formula string, and a flag/reason for any null periods (growth left blank for those).

&#x20;   error\_handling: If growth\_type is missing or invalid, raise an error asking the caller to specify MoM or YoY — never default silently. If ward/category combination has no rows, raise a clear error.

