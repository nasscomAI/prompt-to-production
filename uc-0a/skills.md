role: >
  Civic Complaint Assessment skillset containing defined abilities to evaluate single complaints (`classify_complaint`) and process bulk complaint data (`batch_classify`).

intent: >
  Provide accurate, reproducible classification of civic complaints, mapping raw descriptions to precise categories, priorities, and cited reasons across entire CSV datasets.

context: >
  Reads from input city data files (e.g., data/city-test-files/test_[your-city].csv) and outputs structured data to results_[your-city].csv. Must rely strictly on the text provided.

enforcement:
  - "`classify_complaint` must strictly assign a category from the allowed exact strings: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other."
  - "`classify_complaint` must categorize priority as Urgent if severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present."
  - "`classify_complaint` must supply a one-sentence reason citing specific words and apply the NEEDS_REVIEW flag if genuinely ambiguous."
  - "`batch_classify` must correctly perform row-by-row classification of an input CSV file and write an aggregate results CSV."
