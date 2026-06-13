## `classify_complaint`

One complaint row in → category + priority + reason + flag out.

Given a single row with a `description` field:
1. Assign `category` from the exact allowed list: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
2. Assign `priority` — `Urgent` if the description contains any severity keyword (`injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`), otherwise `Standard`.
3. Write a one-sentence `reason` that cites specific words from the description.
4. If the correct category is genuinely unclear, set `flag` to `NEEDS_REVIEW` and `category` to `Other`.

## `batch_classify`

Reads input CSV, applies `classify_complaint` per row, writes output CSV.

1. Read the input CSV (`--input` argument). Skip the `category` and `priority_flag` columns if present.
2. For each row, invoke `classify_complaint`.
3. Write the output CSV (`--output` argument) with columns: `description`, `category`, `priority`, `reason`, `flag`.
