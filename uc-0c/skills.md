skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the budget CSV, validates required columns, and reports all null actual\_spend rows with their notes.

&#x20;   input: CSV file containing period, ward, category, budgeted\_amount, actual\_spend, and notes.

&#x20;   output: Validated dataset with null rows identified and their reasons.

&#x20;   error\_handling: If required columns are missing or the file is unreadable, report the error and stop.



&#x20; - name: compute\_growth

&#x20;   description: Computes the requested growth type for the specified ward and category without aggregation.

&#x20;   input: Validated dataset, ward, category, and explicit growth\_type such as MoM.

&#x20;   output: Per-period table containing actual spend, formula used, growth result, and null flags where applicable.

&#x20;   error\_handling: If ward, category, or growth\_type is missing or invalid, refuse to calculate rather than guessing.

