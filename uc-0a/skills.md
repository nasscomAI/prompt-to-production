skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classifies one complaint using its description and returns a category, priority, reason, and review flag.

&#x20;   input: A dictionary representing one CSV complaint row, including complaint\_id and description fields.

&#x20;   output: A dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: If the row or description is missing or ambiguous, return category Other, priority Normal, a reason explaining the problem, and flag NEEDS\_REVIEW.



&#x20; - name: batch\_classify

&#x20;   description: Reads a complaint CSV, classifies every row, and writes a results CSV without stopping on individual bad rows.

&#x20;   input: Input CSV file path and output CSV file path supplied as command-line arguments.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for every input row.

&#x20;   error\_handling: Invalid or incomplete rows are converted into reviewable output rows with flag NEEDS\_REVIEW; unexpected row-level errors must not prevent processing of remaining rows.

