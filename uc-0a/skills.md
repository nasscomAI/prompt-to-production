skills:



&#x20; - name: classify\_complaint

&#x20;   description: Classifies one citizen complaint into category, priority, reason, and review flag.

&#x20;   input: One complaint row as a dictionary containing complaint\_id and description.

&#x20;   output: Dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: Missing or invalid descriptions produce Other, Standard, a one-sentence reason, and NEEDS\_REVIEW; ambiguous categories are also flagged for review.



&#x20; - name: batch\_classify

&#x20;   description: Reads a complaint CSV, applies classify\_complaint to every row, and writes the classification results to an output CSV.

&#x20;   input: Input CSV path and output CSV path.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for every input row.

&#x20;   error\_handling: Individual bad rows do not stop the batch; failed rows are written as Other, Standard with NEEDS\_REVIEW, while the remaining rows continue to be processed.

