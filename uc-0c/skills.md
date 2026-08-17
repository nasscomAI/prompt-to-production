skills:



&#x20; - name: load\_dataset

&#x20;   description: Reads the ward budget CSV, validates required columns, counts null actual\_spend values, and reports every null row with its notes.

&#x20;   input: CSV file path containing period, ward, category, budgeted\_amount, actual\_spend, and notes columns.

&#x20;   output: Validated dataset with rows, required columns, null count, and details of every row where actual\_spend is missing.

&#x20;   error\_handling: If the file cannot be read or required columns are missing, report the input error and stop; never invent missing values.



&#x20; - name: compute\_growth

&#x20;   description: Computes growth for one explicitly selected ward and category at the requested growth type without aggregating across wards or categories.

&#x20;   input: Validated dataset, one ward name, one category name, and an explicitly specified growth type such as MoM.

&#x20;   output: Per-period table containing ward, category, period, actual\_spend, formula, growth result, and null status or reason when actual\_spend is missing.

&#x20;   error\_handling: Refuse when ward, category, or growth type is missing or invalid; flag null actual\_spend rows and do not compute growth for them; refuse any request for all-ward or cross-category aggregation.

