skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classifies a single complaint into category, priority, reason and flag.

&#x20;   input: Complaint row dictionary.

&#x20;   output: Dictionary containing complaint\_id, category, priority, reason and flag.

&#x20;   error\_handling: Returns category Other and flag NEEDS\_REVIEW when classification is ambiguous.



&#x20; - name: batch\_classify

&#x20;   description: Processes an entire CSV file and writes classification results.

&#x20;   input: Input CSV path.

&#x20;   output: Output CSV path containing classified complaints.

&#x20;   error\_handling: Continues processing even if individual rows contain errors.

