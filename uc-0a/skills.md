* # skills:
* # &#x20; - name: classify\_complaint
* # &#x20;   description: Classifies a single citizen complaint description into category, priority, reason, and flag according to the UC-0A schema.
* # &#x20;   input: A single row (dict) with at least a description field, plus any other original CSV columns for context.
* # &#x20;   output: A dict with four fields — category (one of the 10 allowed values), priority (Urgent, Standard, or Low), reason (one sentence citing words from the description), and flag (NEEDS\_REVIEW or blank).
* # &#x20;   error\_handling: If the description is empty, missing, or too vague to support any specific category, output category as Other, priority as Standard, reason explaining why it couldn't be classified, and flag as NEEDS\_REVIEW. Never fabricate a specific category to avoid returning Other.
* # 
* # &#x20; - name: batch\_classify
* # &#x20;   description: Reads the input CSV file row by row, applies classify\_complaint to each row, and writes all results to the output CSV file.
* # &#x20;   input: A file path to the input CSV (with description and other original columns, category and priority\_flag stripped).
* # &#x20;   output: A file path to the output CSV containing all original columns plus category, priority, reason, and flag for every row.
* # &#x20;   error\_handling: If a row is malformed (missing required columns) or the file fails to open, skip that row, log which row and why, and continue processing the rest rather than crashing the whole batch.

