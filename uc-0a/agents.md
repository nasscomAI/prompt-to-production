# agents.md — UC-0A Complaint Classifier (RICE spec)

> Agent: a deterministic Python classifier (`classifier.py`) that reads a
> city complaint CSV whose `category` and `priority_flag` columns have been
> stripped, and emits `complaint_id, category, priority, reason, flag` for
> every row. This file is the contract the code is held to. Every rule below
> is phrased so a reviewer (or a test) can check it with a single assertion
> against `results_*.csv`.

---

## role

A rule-based civic-complaint triage agent. It assigns exactly one taxonomy
category and one priority to each complaint, backed by a one-sentence
justification that quotes the complaint's own words. It is **not** a language
model: it uses keyword precedence plus severity-stem matching, it makes zero
network calls, and it never invents a category that is not in the enum below.

## intent

A correct run produces, for each input row, a result whose `category` is a
member of the fixed 10-value enum, whose `priority` is `Urgent` whenever the
description contains any of the nine severity word-stems, whose `reason` is a
single sentence containing at least one word lifted verbatim from that row's
`description`, and whose `flag` is `NEEDS_REVIEW` precisely when the category
could not be assigned with confidence (empty description, or no taxonomy
keyword matched). Verifiable end state: `python classifier.py --input ... --output ...`
exits 0 and writes one output row per input row.

## context

The agent is allowed to read **only** the columns of the single input CSV
(`complaint_id, date_raised, city, ward, location, description, reported_by,
days_open`). Classification must be derived from the `description` field
alone — `ward`, `city`, `reported_by`, and `days_open` must NOT influence
category or priority (they are excluded explicitly to prevent location-based
guessing). The agent must not call any LLM, API, or network resource, and
must not read files outside its own `uc-0a/` folder and the `data/` input it
is pointed at.

## enforcement

Each rule below is paired with the exact check that proves it holds.

1. **Closed category enum.** `category` MUST be exactly one of these ten
   literal strings — `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`,
   `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
   No synonyms, no casing variants, no pluralised labels (e.g. "Potholes",
   "Garbage", "Drainage", "Roads" are all illegal).
   *Check:* `assert set(row['category'] for row in all_results) <= set(ALLOWED_CATEGORIES)`

2. **Severity overrides priority — stem match, case-insensitive.** `priority`
   MUST be `Urgent` if the description contains ANY of these word-stems:
   `injur`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`,
   `fell`, `collaps` (matched on word boundaries so `child` catches
   `children`, `injury` catches `injured`, `hospital` catches `hospitalised`,
   `collapse` catches `collapsed`, but `fell` does NOT catch `fall`). If none
   match, `priority` MUST be `Standard`. This check is independent of
   category: a Pothole, a Flood, and a Streetlight are all Urgent if a
   severity stem is present.
   *Check:* for every row, `re.search(r'\b(injur|child|school|hospital|ambulance|fire|hazard|fell|collaps)', desc, re.I)` is True iff `priority == 'Urgent'`.

3. **Justification cites real words.** Every output row MUST carry a
   `reason` that is exactly one sentence and that contains at least one token
   (length >= 3) copied verbatim from that same row's `description`
   (case-insensitive). A generic label such as "classified as Pothole" with no
   quoted source word fails this rule.
   *Check:* `assert any(token.lower() in desc.lower() for token in word_tokenize(reason) if len(token) >= 3)`.

4. **No confidence on ambiguity — refuse and flag.** If the `description` is
   empty/missing, OR no taxonomy keyword from the ten categories matches it,
   the agent MUST emit `category='Other'` AND `flag='NEEDS_REVIEW'`. It must
   never fabricate a sub-category ("Tree Hazard", "Park Maintenance",
   "Gas Leak") to force a confident answer.
   *Check:* for every row where no category keyword matches, `category == 'Other' and flag == 'NEEDS_REVIEW'`; and `flag` is blank for every confidently-classified row.

5. **Dual-signal rows resolve by documented precedence, not by guess.** When
   a description carries keywords for two categories (e.g. "Bus stand
   flooded. ... Drain blocked.", or "Heritage zone garbage overflow"), the
   agent MUST pick by a fixed, ordered precedence — Heat Hazard > Heritage
   Damage > Pothole > Drain Blockage > Flooding > Streetlight > Noise > Waste
   > Road Damage > Other — and cite the winning keyword in the `reason`. This
   makes the output deterministic and reproducible across runs.
   *Check:* re-running on the same input produces byte-identical output (`diff` is empty); the cited keyword in `reason` belongs to the precedence-winning category.

6. **Batch resilience.** A single malformed row (missing `description`,
   unparseable field, thrown exception) MUST NOT abort the batch. The agent
   must write a `NEEDS_REVIEW` Other row for that record and continue, so the
   output always contains exactly one row per input row.
   *Check:* `len(output_rows) == len(input_rows)` for every run, even when a row is deliberately corrupted.
