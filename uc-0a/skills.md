skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classify one complaint into the fixed category, priority, reason, and review flag schema.

&#x20;   input: A dictionary containing complaint\_id and complaint description.

&#x20;   output: A dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: Invalid or missing descriptions are classified as Other with flag NEEDS\_REVIEW and a reason explaining that the description is missing or invalid.



&#x20; - name: batch\_classify

&#x20;   description: Read complaint rows from a CSV, classify each row, and write the results to an output CSV.

&#x20;   input: Input CSV path and output CSV path.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for every input row.

&#x20;   error\_handling: Bad rows must not crash the batch; produce a result row with Other and NEEDS\_REVIEW when classification cannot be completed.



