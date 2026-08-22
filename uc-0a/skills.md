# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint row into an exact category, priority, one-sentence cited reason, and optional NEEDS_REVIEW flag.
    input: One dict representing a CSV row with keys including complaint_id and description (string); description is the primary classification evidence.
    output: Dict with keys complaint_id (str), category (one of exactly Pothole/Flooding/Streetlight/Waste/Noise/Road Damage/Heritage Damage/Heat Hazard/Drain Blockage/Other), priority (Urgent/Standard/Low), reason (one sentence citing words from the description), flag (NEEDS_REVIEW or empty string).
    error_handling: If the description contains any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse — case-insensitive), priority is forced to Urgent regardless of category. If the description is missing, empty, or no category fits, return category=Other, priority per keywords, reason citing what evidence exists (or noting absence), and flag=NEEDS_REVIEW. Never raise on bad input; always return a valid-schema dict.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes all results to an output CSV without failing on malformed rows.
    input: Path to a UTF-8 CSV (test_[city].csv) with columns including complaint_id and description; ~15 rows per file.
    output: Writes a CSV at the given output path with one row per input row containing complaint_id, category, priority, reason, flag; returns nothing but prints a summary (rows read, classified, flagged).
    error_handling: Rows with missing complaint_id get id "<missing>"; rows that raise inside classify_complaint are written as category=Other, flag=NEEDS_REVIEW with an error reason instead of aborting the run. Missing input file raises a clear FileNotFoundError before any processing. Output is always produced even if some individual rows fail.
