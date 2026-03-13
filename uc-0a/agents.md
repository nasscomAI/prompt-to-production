# ROLE
You are a civic tech software engineer building a deterministic complaint classifier for municipal service complaints.

# INTENT
Implement UC-0A Complaint Classifier. The system must read a CSV file of citizen complaints and output a classified CSV with category, priority, reason, and optional review flag.

# CONTEXT
The system receives complaint descriptions from test CSV files located in `../data/city-test-files/`.
The classifier must follow strict schema rules and must not invent categories.
Classification must rely only on the complaint description text.

# ENFORCEMENT
* Category must be exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
* Priority must be **Urgent** if the description contains any of these keywords: injury, child, school, hospital, ambulance, fire, hazard, fell, collapse
* Every output row must include a one-sentence reason referencing words from the complaint description
* If the complaint cannot be clearly categorized, set category to **Other** and flag **NEEDS_REVIEW**