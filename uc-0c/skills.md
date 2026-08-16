skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads and validates the ward budget CSV and reports required columns and null actual\_spend rows before analysis.

&#x20;   input: Path to a CSV file containing period, ward, category, budgeted\_amount, actual\_spend, and notes columns.

&#x20;   output: Validated dataset with structured rows, null count, and details including the period, ward, category, and notes for every null actual\_spend row.

&#x20;   error\_handling: If the file is missing, unreadable, missing required columns, or contains invalid data, return an explicit error and do not invent or replace values.



&#x20; - name: compute\_growth

&#x20;   description: Calculates per-period growth for one explicitly requested ward and category using the specified growth type.

&#x20;   input: Validated dataset, one ward, one category, and an explicit growth type such as MoM.

&#x20;   output: Per-period table containing the ward, category, period, actual spend, formula used, growth result, and null status or reason where applicable.

&#x20;   error\_handling: If ward, category, or growth type is missing or ambiguous, refuse to calculate; if actual\_spend is null, flag the row and report its notes reason instead of computing growth.

