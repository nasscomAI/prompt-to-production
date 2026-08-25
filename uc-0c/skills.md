skills:

&#x20; - name: load\_dataset

&#x20;   description: Reads the budget CSV, validates required columns, reports null actual\_spend rows and their reasons, and returns the dataset.

&#x20;   input: CSV file containing period, ward, category, budgeted\_amount, actual\_spend, and notes columns.

&#x20;   output: Validated dataset plus a list of rows where actual\_spend is null and the corresponding notes.

&#x20;   error\_handling: Rejects missing files or required columns and reports null actual\_spend rows without replacing them with invented values.



&#x20; - name: compute\_growth

&#x20;   description: Computes per-period growth for one explicitly requested ward and category using the requested growth type.

&#x20;   input: Validated dataset, one ward, one category, and an explicit growth type such as MoM.

&#x20;   output: Per-period table containing period, actual spend, formula, growth result, and null reason when applicable.

&#x20;   error\_handling: Refuses unspecified or unsupported growth types, refuses cross-ward or cross-category aggregation, and flags rows with null or unusable previous values instead of guessing.

