# Skills for UC-0A
- `classify_complaint`: Reads one complaint row. Uses exact keyword matching for severity (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse -> Urgent). Outputs category, priority, reason, flag.
- `batch_classify`: Reads an input CSV file and processes it row-by-row using `classify_complaint`, then writes to a specified output CSV file.
