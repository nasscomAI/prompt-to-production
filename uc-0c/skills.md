skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the ward budget CSV, validates required columns are present, and reports how many null actual\_spend rows exist and which ones before returning filtered data.

&#x20;   input: A file path (string) to a CSV with columns period, ward, category, budgeted\_amount, actual\_spend, notes; plus a ward name (string) and category name (string) to filter by.

&#x20;   output: A pandas DataFrame filtered to the specified ward and category, sorted by period, plus a printed/logged list of null rows (period, ward, category, notes) found within that filtered subset.

&#x20;   error\_handling: If the CSV is missing any required column, raises a clear error naming the missing column and stops execution. If the specified ward or category does not exist in the dataset, raises an error listing the valid ward/category names instead of silently returning an empty table.



&#x20; - name: compute\_growth

&#x20;   description: Computes MoM or YoY growth percentage for each period of a single ward/category series, showing the formula alongside each computed value, and flags rather than computes rows with null actual\_spend.

&#x20;   input: A filtered DataFrame (single ward, single category, sorted by period) and a growth\_type string that must be exactly "MoM" or "YoY".

&#x20;   output: A DataFrame/CSV with columns period, ward, category, budgeted\_amount, actual\_spend, growth\_pct, formula\_used, and a status column marking rows as "computed" or "flagged\_null" with the null reason from notes.

&#x20;   error\_handling: If growth\_type is missing or not one of "MoM"/"YoY", raises an error and refuses to compute rather than defaulting to one. If a row's previous period (for MoM) or same month last year (for YoY) is itself null, the current row is also flagged rather than computed, since growth cannot be derived from a missing baseline.

