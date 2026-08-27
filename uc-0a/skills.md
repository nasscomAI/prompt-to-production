# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into taxonomy and assigns priority with justification.
    input: A single complaint description string.
    output: A dictionary/struct with category (one of 10 allowed), priority (Urgent/Standard/Low), reason (citing words), and flag.
    error_handling: Set flag to 'NEEDS_REVIEW' and category to 'Other' if the description is genuinely ambiguous.

  - name: batch_classify
    description: Reads an input CSV of complaints and writes the classified results to an output CSV.
    input: File path to input CSV (../data/city-test-files/test_[city].csv).
    output: Creates/overwrites output CSV file (uc-0a/results_[city].csv) with classified results.
    error_handling: Skip malformed CSV rows and log errors.
