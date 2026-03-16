# 

\# skills.md — UC-0A Complaint Classifier



skills:

&#x20; - name: classify\_complaint

&#x20;   description: Classifies a single citizen complaint by extracting category, priority, reason, and review flag based strictly on the complaint text.

&#x20;   input: A string containing the complaint description.

&#x20;   output: A dictionary with fields: category (string), priority (string), reason (string), flag (string or empty).

&#x20;   error\_handling: If input is missing, empty, or too ambiguous to categorize, return category="Other", flag="NEEDS\_REVIEW", reason="Insufficient information to classify".



&#x20; - name: batch\_classify

&#x20;   description: Reads an input CSV of citizen complaints, applies classify\_complaint to each row, and writes results to an output CSV.

&#x20;   input: input\_path (string) - path to input CSV file, output\_path (string) - path for output CSV file.

&#x20;   output: Creates a CSV file with columns: category, priority, reason, flag.

&#x20;   error\_handling: Skip rows that cause parsing errors and log them to console. Ensure output CSV is still written for successfully processed rows.

