skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classifies one complaint row into category, priority, reason, and flag.

&#x20;   input: One complaint row as a dictionary containing the complaint information.

&#x20;   output: A dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: If the complaint is invalid or genuinely ambiguous, use category Other and flag NEEDS\_REVIEW.



&#x20; - name: batch\_classify

&#x20;   description: Reads complaint rows from a CSV, classifies each row, and writes the results to an output CSV.

&#x20;   input: Input CSV path and output CSV path.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for each row.

&#x20;   error\_handling: Flag null or bad rows instead of crashing and continue processing remaining rows.

