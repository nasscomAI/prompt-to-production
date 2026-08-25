\# skills.md



skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classify one citizen complaint into an allowed category and priority with a justified reason and review flag.

&#x20;   input: One complaint row as a dictionary containing complaint\_id and description.

&#x20;   output: A dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: If the description is missing, invalid, or genuinely ambiguous, return a safe classification using Other and NEEDS\_REVIEW without crashing.



&#x20; - name: batch\_classify

&#x20;   description: Read complaint rows from a CSV, classify each row, and write the classification results to an output CSV.

&#x20;   input: Input CSV path and output CSV path.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for every input row.

&#x20;   error\_handling: Continue processing when an individual row is invalid, record a review flag for that row, and still produce the output CSV.

