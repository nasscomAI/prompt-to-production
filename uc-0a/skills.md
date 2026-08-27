# UC-0A Skills

This document defines the skills required to correctly execute **UC-0A — Complaint Classifier**, enforcing schema, priority rules, and ambiguity handling exactly as specified in the README.

---

## classify_complaint

**Purpose**  
Classifies a single citizen complaint into structured output fields.

**Output Fields**
- `category`: Must be one of the approved taxonomy values only.
- `priority`: Urgent, Standard, or Low.
- `reason`: Exactly one sentence citing words from the complaint.
- `flag`: `NEEDS_REVIEW` only if the category is genuinely ambiguous.

**Allowed Categories**
Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other

**Urgent Severity Keywords**  
injury, child, school, hospital, ambulance, fire, hazard, fell, collapse

---

## batch_classify

Processes an input CSV by applying `classify_complaint` to each row and writing a compliant output CSV.

**Input**  
`../data/city-test-files/test_<city>.csv`

**Output**  
`uc-0a/results_<city>.csv`
