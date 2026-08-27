# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: >
      Classifies a single citizen complaint row into an allowed category and priority, emits a one-sentence
      reason grounded in the complaint text, and sets NEEDS_REVIEW when the taxonomy match is ambiguous.
    input: >
      One record (dict or row object) containing at least a complaint description field (e.g. `description`
      or the column name used in the city CSV). Optional other non-label columns may be present; do not
      read withheld ground-truth columns if they appear in development data.
    output: >
      A structured object with exactly: `category` (string), `priority` (string), `reason` (string),
      `flag` (string: `NEEDS_REVIEW` or empty). `category` ∈ {Pothole, Flooding, Streetlight, Waste, Noise,
      Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other}. `priority` ∈ {Urgent, Standard, Low}.
    error_handling: >
      If description is missing or empty, set category `Other`, priority `Standard`, reason stating that no
      description was provided, flag `NEEDS_REVIEW`. If text is present but ambiguous, prefer `Other` plus
      `NEEDS_REVIEW` over guessing a narrow category. Never output a category string outside the allowed list.

  - name: batch_classify
    description: >
      Reads a city test CSV, runs `classify_complaint` on each data row, and writes a results CSV with
      predicted columns aligned to the UC-0A evaluation schema.
    input: >
      Paths: input CSV matching `../data/city-test-files/test_[your-city].csv` (or equivalent), UTF-8,
      one row per complaint. Rows exclude ground-truth `category` and `priority_flag` in the official test
      harness; implementation must only use fields provided per row.
    output: >
      CSV at `uc-0a/results_[your-city].csv` (or `--output` path per `classifier.py`) including at least:
      `category`, `priority`, `reason`, `flag` (and any identifier columns required for grading). Column
      names and order must match what `classifier.py` / rubric expect.
    error_handling: >
      Skip or fail fast with a clear error if the file is unreadable. On per-row failure after retries,
      write a row with `Other`, `Standard` or `Low` as appropriate, reason noting processing failure,
      and `NEEDS_REVIEW`. Log row index for debugging. Preserve row order unless the rubric requires otherwise.

alignment:
  agent_spec: "agents.md"
  enforcement: >
    batch_classify MUST delegate per-row logic to classify_complaint (or equivalent shared function) so
    taxonomy and priority rules do not drift between single-row and batch paths.
