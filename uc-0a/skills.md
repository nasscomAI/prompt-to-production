# skills.md — UC-0A Complaint Classifier

Two callable skills exposed by `classifier.py`. Both are pure-standard-library
Python 3.9, deterministic, and make no network or LLM calls.

---

## skill: `classify_complaint`

**description:** Classifies a single civic-complaint record into one taxonomy
category plus a priority, and writes a one-sentence justification that quotes
the complaint's own description.

**input:** A `dict` representing one CSV row. The only keys it consults are
`complaint_id` (string; falls back to `"UNKNOWN"` if absent) and
`description` (string; the free-text citizen complaint). Extra keys
(`ward`, `city`, `days_open`, ...) are ignored on purpose so classification
is driven by the description alone.

**output:** A `dict` with exactly these keys:
`complaint_id` (string),
`category` (one of the 10-value enum: Pothole, Flooding, Streetlight, Waste,
Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
`priority` (`Urgent` if any severity stem — injur/child/school/hospital/
ambulance/fire/hazard/fell/collaps — is present, else `Standard`),
`reason` (a single sentence containing at least one word copied verbatim
from the input `description`), and
`flag` (the empty string `""`, or `"NEEDS_REVIEW"`).

**error_handling:**
- Empty / missing `description` -> returns `category='Other'`,
  `priority='Standard'`, `flag='NEEDS_REVIEW'`, and a `reason` that cites the
  missing field. Does not raise.
- Description present but matching no taxonomy keyword -> returns
  `category='Other'`, `flag='NEEDS_REVIEW'`, and a `reason` quoting the first
  few words of the description. Does not raise.
- Any unexpected exception inside the caller is caught by `batch_classify`
  (see below), which substitutes a `NEEDS_REVIEW` row so the batch continues.

---

## skill: `batch_classify`

**description:** Reads a city complaint CSV, runs `classify_complaint` on
every row, and writes a results CSV with the header
`complaint_id,category,priority,reason,flag` — producing exactly one output
row per input row even when individual rows fail.

**input:** Two filesystem paths as strings:
`input_path` (the `test_[city].csv` file, read with `csv.DictReader` so
quoted descriptions containing commas are handled correctly) and
`output_path` (where `results_[city].csv` is written). Relative paths that
cannot be found relative to the current working directory are retried
relative to the repo root (located via `Path(__file__).resolve().parent.parent`),
so both `python uc-0a/classifier.py --input data/...` from the repo root and
`python classifier.py --input ../data/...` from inside `uc-0a/` work.

**output:** Writes the output CSV (UTF-8, one row per input row, header
`complaint_id,category,priority,reason,flag`) and returns the list of result
dicts. Every returned dict satisfies the `classify_complaint` output contract
above.

**error_handling:**
- A row missing its `complaint_id` is assigned a synthetic id `ROW_<index>`.
- Each row is classified inside a `try/except`; any exception produces a
  `NEEDS_REVIEW` Other row whose `reason` records the exception class and
  message, so one bad row never aborts the batch.
- The output file is always created (even if every row failed), and the
  output parent directory is created with `mkdir(parents=True, exist_ok=True)`
  if it does not yet exist.
