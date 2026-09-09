\# UC-0C Skills



skills:

&#x20; - name: load\_budget\_data

&#x20;   description: Loads ward-level infrastructure budget data from the supplied CSV and validates the required fields.

&#x20;   input: A path to ward\_budget.csv containing period, ward, category, budgeted\_amount, actual\_spend, and notes fields.

&#x20;   output: Structured budget records containing the source period, ward, category, and actual spend.

&#x20;   error\_handling: If the file is missing, malformed, or required fields are absent, report the error and stop without inventing values.



&#x20; - name: calculate\_mom\_growth

&#x20;   description: Calculates month-over-month actual-spend growth for one requested ward and category.

&#x20;   input: Validated budget records plus ward, category, and growth-type parameters.

&#x20;   output: CSV rows containing ward, category, previous period, current period, previous actual spend, current actual spend, and growth percentage.

&#x20;   error\_handling: Do not calculate from missing actual spend or ambiguous data; report the limitation rather than estimating or silently aggregating records.

