# skills.md — UC-0A Complaint Classifier

## classify_complaint

Classify a single citizen complaint using the required taxonomy and priority rules.

### Input

* `description`: the citizen's complaint text.

### Output

Return:

* `category`
* `priority`
* `reason`
* `flag`

### Rules

1. `category` must be exactly one of:

   * Pothole
   * Flooding
   * Streetlight
   * Waste
   * Noise
   * Road Damage
   * Heritage Damage
   * Heat Hazard
   * Drain Blockage
   * Other

2. `priority` must be exactly one of:

   * Urgent
   * Standard
   * Low

3. Set `priority` to `Urgent` when the description contains any of these severity keywords, case-insensitive:
   `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`.

4. If no severity keyword is present, assign `Standard` unless the complaint clearly indicates a lower-priority issue, in which case assign `Low`.

5. `reason` must be exactly one sentence and must cite specific words or phrases from the description.

6. If the description is genuinely ambiguous, select the best-supported allowed category and set `flag` to `NEEDS_REVIEW`. Do not invent facts to resolve ambiguity.

7. If no allowed category is supported by the description, use `Other`.

## batch_classify

Classify every complaint in an input dataset using `classify_complaint`.

### Input

A collection of citizen complaint records containing complaint descriptions.

### Output

Produce exactly one result for every input record with:
`category,priority,reason,flag`

### Rules

* Preserve the number and order of input records.
* Apply the same taxonomy, severity, evidence, and ambiguity rules to every record.
* Do not drop or duplicate records.
* Validate every category and priority against the allowed values before writing the output.
* Leave `flag` blank when the complaint is not genuinely ambiguous.
* Ensure every `reason` is one sentence and supported by the description.
