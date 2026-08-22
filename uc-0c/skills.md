skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the budget CSV, validates required columns, and reports null actual\_spend rows before calculations.

&#x20;   input: CSV file path containing period, ward, category, budgeted\_amount, actual\_spend, and notes columns.

&#x20;   output: Validated list of budget records plus null-row information including period, ward, category, and notes.

&#x20;   error\_handling: Rejects missing required columns or invalid CSV data and never silently converts null actual\_spend values into zero.



&#x20; - name: compute\_growth

&#x20;   description: Computes per-period growth for one ward and category using the explicitly requested growth type.

&#x20;   input: Validated budget records, one ward, one category, and an explicit growth type such as MoM.

&#x20;   output: Per-period table containing ward, category, period, actual\_spend, growth\_type, formula, growth\_percent, and flag.

&#x20;   error\_handling: Refuses missing growth types and cross-ward or cross-category aggregation; flags rows when current or previous actual\_spend is null instead of calculating a value.

