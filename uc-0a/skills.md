# skills.md — UC-0A Complaint Classifier

## classify_complaint

Purpose:
Classify one citizen complaint row into the required UC-0A output fields.

Input:

* One complaint row containing a complaint description and complaint_id when available.

Output:

* complaint_id
* category
* priority
* reason
* flag

Rules:

* Use only the exact UC-0A categories: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
* Use only the priority values: Urgent, Standard, Low.
* Set priority to Urgent if the description contains any of these severity keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse.
* The reason must be exactly one sentence and must cite specific words from the complaint description.
* If the category is genuinely ambiguous, use category Other and set flag to NEEDS_REVIEW.
* If the category is not genuinely ambiguous, leave flag blank.
* Never invent a category, sub-category, or information not present in the description.

## batch_classify

Purpose:
Classify every complaint in an input CSV and write the results to an output CSV.

Input:

* A CSV file containing complaint rows.

Process:

1. Read the input CSV.
2. Apply classify_complaint to every row.
3. Preserve the complaint_id when available.
4. Produce category, priority, reason, and flag for every row.
5. Handle missing or malformed rows without crashing the entire batch.
6. Write the classification results to the specified output CSV.

Output:
A CSV containing:

* complaint_id
* category
* priority
* reason
* flag
