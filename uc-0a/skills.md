skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classify one citizen complaint into an allowed category and priority with a description-grounded reason and ambiguity flag.

&#x20;   input: A complaint row as a dictionary containing complaint\_id and description plus optional complaint metadata.

&#x20;   output: A dictionary containing complaint\_id, category, priority, reason, and flag.

&#x20;   error\_handling: Invalid or missing descriptions produce category Other, priority Standard, a reason explaining the missing description, and NEEDS\_REVIEW.



&#x20; - name: batch\_classify

&#x20;   description: Read complaint rows from an input CSV, classify each row, and write the results to an output CSV.

&#x20;   input: Input CSV path containing complaint rows and output CSV path for classification results.

&#x20;   output: CSV containing complaint\_id, category, priority, reason, and flag for every input row.

&#x20;   error\_handling: Bad rows are not allowed to stop the batch; failed rows are written as Other, Standard, with NEEDS\_REVIEW and an explanatory reason.

