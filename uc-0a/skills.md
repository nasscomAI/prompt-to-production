# UC-0A Skills

## Skills Definition

### classify_complaint
**Description:** Classify a single complaint row into category, priority level, and justification.

**Input:** 
- Type: `dict`
- Format: `{"complaint_id": str, "description": str, "latitude": float, "longitude": float}`

**Output:**
- Type: `dict`
- Format: `{"complaint_id": str, "category": str, "priority": str, "reason": str, "flag": str}`
- Fields:
  - `category`: Exactly one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other
  - `priority`: Urgent, Standard, or Low
  - `reason`: One sentence citing specific words from the description
  - `flag`: "NEEDS_REVIEW" if ambiguous, empty string otherwise

**Error Handling:** 
- If description is empty or null, set category to "Other" and flag to "NEEDS_REVIEW"
- If multiple categories could apply, classify to most specific match; flag "NEEDS_REVIEW" if genuine ambiguity
- If description contains severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), must set priority to "Urgent"

### batch_classify
**Description:** Read input CSV, classify each complaint row, and write results to output CSV.

**Input:**
- Type: File path (str)
- Format: CSV with columns: complaint_id, date_raised, city, ward, location, description, reported by, days_open 
- Location: `../data/city-test-files/test_[city].csv`

**Output:**
- Type: File path (str)
- Format: CSV with columns: complaint_id, date_raised, city, ward, location, description, category, priority, reason, flag
- Location: `uc-0a/results_[city].csv`

**Error Handling:**
- If input file does not exist, raise clear error message
- If a row fails to classify, log error and output row with category="Other", priority="Standard", reason="Classification failed", flag="NEEDS_REVIEW"
- Process all rows even if some fail; do not crash on malformed input
- Write output file even if partial classification succeeds
