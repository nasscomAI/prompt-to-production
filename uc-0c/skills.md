\- name: load\_dataset

&#x20; description: Reads the ward budget CSV dataset, validates required columns, and identifies null values.

&#x20; input:

&#x20;   type: string

&#x20;   format: file path to CSV dataset

&#x20; output:

&#x20;   type: object

&#x20;   format: validated dataset with metadata including null row details

&#x20; error\_handling:

&#x20;   - If file path is invalid, return an error and stop execution

&#x20;   - If required columns are missing, return an error specifying missing columns

&#x20;   - If null values are present in actual\_spend, identify and report all such rows along with notes before returning dataset



\- name: compute\_growth

&#x20; description: Computes month-over-month (MoM) growth for a specific ward and category and returns a per-period table.

&#x20; input:

&#x20;   type: object

&#x20;   format: dataset along with ward, category, and growth\_type parameters

&#x20; output:

&#x20;   type: table

&#x20;   format: per-period rows including actual spend, computed growth, and formula used

&#x20; error\_handling:

&#x20;   - If ward or category is not found, return an error

&#x20;   - If growth\_type is missing or invalid, refuse to compute and ask for valid input

&#x20;   - If null values are encountered for a period, do not compute growth for that period and flag it with reason from notes

&#x20;   - If computation attempts aggregation across wards or categories, refuse execution

