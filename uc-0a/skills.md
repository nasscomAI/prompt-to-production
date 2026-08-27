# UC-0A Complaint Classifier — Skills Definition

## Skill 1: `classify_complaint`

**Purpose**: Classifies a single citizen complaint row into category, priority, reason, and flag.

**Input**: A dictionary representing one CSV row with fields: `complaint_id`, `description`, `location`, `ward`, `days_open`, etc.

**Output**: A dictionary with four keys: `category`, `priority`, `reason`, `flag`.

**Rules applied**:
- Category is determined by keyword matching against the description using a priority-ordered rule chain:
  1. `pothole` → Pothole
  2. `flood`, `flooded`, `waterlog`, `standing in water`, `knee-deep` → Flooding
  3. `streetlight`, `lights out`, `dark at night`, `flickering`, `sparking` → Streetlight
  4. `drain`, `manhole` → Drain Blockage
  5. `garbage`, `waste`, `dead animal`, `overflowing`, `bins` → Waste
  6. `noise`, `music`, `loud` → Noise
  7. `cracked`, `sinking`, `footpath`, `tiles broken`, `road surface` → Road Damage
  8. `heritage` (only when not a lighting/streetlight issue) → Heritage Damage
  9. `heat`, `sunstroke` → Heat Hazard
  10. No match → Other (with `NEEDS_REVIEW` flag)
- Priority is `Urgent` if any severity keyword (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`) is found; otherwise `Standard`.
- Reason cites the exact words from the description that triggered the classification.
- Flag is `NEEDS_REVIEW` only when category is `Other` or multiple categories match equally.

**Error handling**: If description is empty or missing, returns `Other` with `NEEDS_REVIEW`.

---

## Skill 2: `batch_classify`

**Purpose**: Reads an input CSV file, invokes `classify_complaint` for each row, and writes the enriched output CSV.

**Input**: `input_csv_path` (string), `output_csv_path` (string).

**Output**: CSV file at `output_csv_path` with original columns plus `category`, `priority`, `reason`, `flag`.

**Behaviour**:
- Preserves all original CSV fields in order.
- Appends classification columns after the last original column.
- Prints a summary line: "Classified N complaints. Urgent: X, Standard: Y, NEEDS_REVIEW: Z".

**Error handling**: Exits with error message if input file is missing or has unexpected schema.
