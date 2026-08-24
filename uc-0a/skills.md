# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single civic complaint row into one exact category, assigns a
      priority level using severity keyword matching, generates a one-sentence reason
      citing words from the description, and sets a NEEDS_REVIEW flag when the
      category cannot be determined with confidence.
    input: >
      A Python dict representing one CSV row with at minimum the keys:
      complaint_id (str), description (str). Additional keys are passed through
      unchanged.
    output: >
      A Python dict with keys: complaint_id (str, unchanged), category (str, one of
      the 10 allowed values), priority (str: Urgent | Standard | Low), reason (str,
      one sentence), flag (str: "NEEDS_REVIEW" or "").
    error_handling: >
      If description is missing or empty, set category to Other, priority to Low,
      reason to "Description field is empty — cannot classify.", flag to NEEDS_REVIEW.
      Never raise an exception; always return a valid output dict.

  - name: batch_classify
    description: >
      Reads an input CSV file of complaint rows, applies classify_complaint to every
      row, and writes a results CSV containing all output fields. Rows that cause
      unexpected errors are written with category Other, priority Low, and flag
      NEEDS_REVIEW so the pipeline never crashes silently.
    input: >
      input_path (str): path to a UTF-8 CSV file with at minimum columns
      complaint_id and description. output_path (str): path where the results
      CSV will be written.
    output: >
      A UTF-8 CSV file at output_path with columns: complaint_id, category,
      priority, reason, flag. One row per input row. A summary line is printed
      to stdout: total rows processed, Urgent count, NEEDS_REVIEW count.
    error_handling: >
      If input file is missing, raise FileNotFoundError immediately with a clear
      message. If an individual row fails for any reason, catch the exception,
      log a warning to stderr with the complaint_id, and write that row as
      Other / Low / NEEDS_REVIEW before continuing.

# ── Taxonomy Reference (exact strings required) ──────────────────────────────
# Pothole         – surface depressions, holes, pitting in road surface
# Flooding        – inundation of roads, underpasses, or buildings by water
# Streetlight     – faulty, missing, or damaged street lighting
# Waste           – garbage, solid waste overflow, uncollected rubbish
# Noise           – noise pollution from construction, vehicles, generators
# Road Damage     – road collapse, cracking, cave-in, damaged surface (non-pothole)
# Heritage Damage – damage or pollution affecting a designated heritage site or zone
# Heat Hazard     – extreme heat exposure risk, lack of shade or water
# Drain Blockage  – blocked or overflowing storm drains, sewers, drainage channels
# Other           – does not clearly fit any above category
#
# ── Severity Keywords (ANY match → Urgent) ───────────────────────────────────
# injury, injured, hospitalised, hospitalized, child, school, hospital,
# ambulance, fire, hazard, fell, collapse, collapsed, lives at risk,
# danger, emergency
