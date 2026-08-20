\# UC-0C skills.md



skills:

&#x20; - name: load\_dataset

&#x20;   description: >

&#x20;     Reads the ward budget CSV, validates the required columns, and reports

&#x20;     the total row count and every row with a null actual\_spend value.



&#x20;   input: >

&#x20;     A CSV file path containing period, ward, category, budgeted\_amount,

&#x20;     actual\_spend, and notes columns.



&#x20;   output: >

&#x20;     A tuple containing all CSV rows and the list of rows whose

&#x20;     actual\_spend value is null.



&#x20;   error\_handling: >

&#x20;     Reject a missing file or missing required columns with a clear error.

&#x20;     Do not silently replace missing actual\_spend values.



&#x20; - name: compute\_growth

&#x20;   description: >

&#x20;     Calculates per-period growth for exactly one ward and one category

&#x20;     using the explicitly requested MoM or YoY formula.



&#x20;   input: >

&#x20;     Loaded CSV rows, an exact ward name, an exact category name, and an

&#x20;     explicit growth type of MoM or YoY.



&#x20;   output: >

&#x20;     A per-period table containing ward, category, period, actual\_spend,

&#x20;     growth\_type, formula, growth, flag, and null\_reason.



&#x20;   error\_handling: >

&#x20;     Refuse missing or invalid growth types. Flag null actual\_spend values,

&#x20;     missing comparison values, and zero comparison values as NEEDS\_REVIEW.

&#x20;     Never invent values or silently select a formula.
