# Skills — UC-0A Complaint Classifier

## classify_complaint
**Input:** one complaint `description` string
**Output:** dict with `category`, `priority`, `reason`, `flag`
**Behavior:**
- Matches description text against a fixed keyword-to-category map.
- If exactly one category's keywords match, uses that category, flag blank.
- If zero categories match, category = "Other", flag = NEEDS_REVIEW.
- If two or more categories match, picks the first by priority order but
  sets flag = NEEDS_REVIEW and names the competing categories in `reason`.
- Priority = Urgent if any severity keyword (injury, child, school,
  hospital, ambulance, fire, hazard, fell, collapse) appears in the text,
  else Standard.
- Reason always names the specific matched keyword(s), never a generic phrase.

## batch_classify
**Input:** `input_path` (CSV with a `description` column), `output_path`
**Output:** writes a new CSV = all original columns + category, priority,
reason, flag
**Behavior:**
- Reads all rows with csv.DictReader.
- Calls classify_complaint on each row's description.
- Preserves every original column and appends the four new ones.
- Writes result with csv.DictWriter, one row per input row.
- Prints a one-line summary of rows processed.
