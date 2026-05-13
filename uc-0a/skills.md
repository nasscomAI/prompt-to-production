# Skills for UC-0A Complaint Classifier

## classify_complaint

This skill classifies a single citizen complaint description.

Input:
A complaint description text.

Output:
- category
- priority
- reason
- flag

Rules:
The category must be one of the allowed values such as Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, or Other.

The priority becomes Urgent if severity keywords appear such as injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse.

The reason explains which words in the complaint description triggered the classification.

If the complaint is unclear, the flag NEEDS_REVIEW is added.


## batch_classify

This skill processes multiple complaints from a CSV file.

Steps:
1. Read the input CSV file containing complaint descriptions.
2. Apply the classify_complaint function to each row.
3. Generate category, priority, reason, and flag fields.
4. Write the results into a new output CSV file.