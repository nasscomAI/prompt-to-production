skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the budget CSV, validates required columns, and reports null actual\_spend rows before returning the dataset.

&#x20;   input: CSV file path containing period, ward, category, budgeted\_amount, actual\_spend, and notes columns.

&#x20;   output: Structured dataset plus validation information and a list of rows with null actual\_spend values.

&#x20;   error\_handling: Rejects missing files or required columns and reports null rows without replacing or guessing their values.



&#x20; - name: compute\_growth

&#x20;   description: Computes growth for one explicitly requested ward and category using the explicitly requested growth type.

&#x20;   input: Structured dataset, ward string, category string, and growth\_type string.

&#x20;   output: Per-period table containing ward, category, period, actual\_spend, growth\_type, formula, growth, and null/review information.

&#x20;   error\_handling: Refuses missing or unsupported growth types, refuses cross-ward or cross-category aggregation, and flags periods affected by null actual\_spend values.



