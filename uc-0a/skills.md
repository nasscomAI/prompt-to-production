# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: normalize_row
    description: Normalize and validate an input CSV row into a dict with
      required fields and trimmed text.
    input: A CSV row (mapping of column-name to string) — expects at least
      `complaint_id` and `description`. Other fields (ward, timestamp) are
      optional and must be copied as-is when present.
    output: dict with keys: `complaint_id` (string), `description` (trimmed
      string or empty), plus any copied fields.
    error_handling: If `complaint_id` is missing, generate a string id prefixed
      with `MISSING_ID_<row_index>` and set `flag` to `MISSING_FIELDS` later in
      the pipeline. Do NOT raise — always return a dict so batch processing
      continues.

  - name: map_category
    description: Map a complaint description to one canonical category using
      deterministic keyword matching and priority of categories.
    input: `description` string (trimmed, lowercased for matching).
    output: One of: `Pothole`, `Flooding`, `Garbage`, `Streetlight`, `WaterLeak`, `TreeIssue`, `Encroachment`, `Noise`, `Other`.
    error_handling: If no keywords match, return `Other` and signal that the
      calling function should set `flag` to `NEEDS_REVIEW`.
    notes: Category matching precedence (first match wins):
      - Pothole: keywords `pothole`, `sinkhole`, `big hole`
      - Flooding: `flood`, `waterlogging`, `water logged`, `sea of water`
      - Garbage: `garbage`, `trash`, `waste`, `dump`, `dumping`
      - Streetlight: `streetlight`, `lamp`, `light not working`, `no light`
      - WaterLeak: `leak`, `leaking pipe`, `water leak`, `pipe burst`
      - TreeIssue: `fallen tree`, `tree fallen`, `overhanging branch`, `tree branch`
      - Encroachment: `encroach`, `encroachment`, `unauthorized structure`, `shop extension`
      - Noise: `noise`, `loud music`, `honking`, `construction noise`

  - name: map_priority
    description: Determine priority level (`Urgent`, `High`, `Normal`) from
      description using injury and impact keywords.
    input: `description` string (trimmed, lowercased for matching).
    output: `Urgent` | `High` | `Normal`.
    error_handling: Always return a priority; do not raise. If input empty,
      return `Normal` and let the caller set `flag`.
    rules:
      - Urgent if any injury keywords present: `injury`, `injured`, `child`, `kid`, `school`, `hospital`, `fire`, `electrocution`, `gas leak`, `drowning`, `death`.
      - High if any impact keywords present and no injury keywords: `blocked road`, `major traffic`, `large-scale flooding`, `collapse`, `fallen tree`, `no water supply`.
      - Otherwise Normal.

  - name: build_reason
    description: Construct a concise `reason` string that quotes the exact
      word or short phrase from the original description that triggered the
      decision. Must be <= 120 characters.
    input: original `description` string, list of matched trigger phrases.
    output: `reason` string (<=120 chars) quoting at least one trigger.
    error_handling: If no trigger phrase available (e.g., empty description),
      return a short explanatory reason like `description missing`.

  - name: classify_complaint
    description: Combine the smaller skills to classify one row and produce
      the final output dict matching `agents.md` intent.
    input: normalized row dict with `complaint_id` and `description`.
    output: dict with keys: `complaint_id`, `category`, `priority`, `reason`, `flag`.
    behavior:
      - If `description` missing/empty/whitespace: return `category` = `Other`,
        `priority` = `Normal`, `flag` = `MISSING_FIELDS`, and `reason` =
        `description missing`.
      - Else: call `map_category`, `map_priority`, build `reason` from matched
        phrases. If category is `Other` because of no matches, set `flag` = `NEEDS_REVIEW` and include `uncertain mapping` in the `reason`.
      - Ensure `reason` includes at least one exact substring from the
        original `description` and is <= 120 chars.

  - name: batch_classify
    description: Read input CSV, call `classify_complaint` for each row, and
      write an output CSV with the result columns.
    input: `input_path` (path to CSV with header), `output_path` (path to write results)
    output: Writes a CSV with header: `complaint_id,category,priority,reason,flag` and returns nothing.
    error_handling: Continue on row errors. For rows that fail to parse,
      write a result row with `complaint_id` if available, `category`=`Other`,
      `priority`=`Normal`, `reason` describing the error, and `flag`=`NEEDS_REVIEW`.
    notes: Must not crash on bad rows; must produce an output file even if some
      rows fail.

examples:
  - input_row: {complaint_id: "123", description: "Large pothole outside school, child fell"}
    expected_output: {complaint_id: "123", category: "Pothole", priority: "Urgent", reason: "child fell", flag: ""}

  - input_row: {complaint_id: "124", description: "Dust and garbage dumped near market"}
    expected_output: {complaint_id: "124", category: "Garbage", priority: "Normal", reason: "garbage dumped", flag: ""}

test_guidance:
  - Provide unit tests that call `map_category`, `map_priority`, and
    `build_reason` with representative inputs and check exact outputs.
  - Create a small `test_sample.csv` (3-5 rows) and assert `batch_classify`
    produces `results_sample.csv` matching expected rows.

implementation_notes:
  - Keep matching case-insensitive but preserve original text in `reason`.
  - Use simple substring matching (no ML) to keep determinism and testability.
  - Limit `reason` to 120 characters by truncating but ensuring a trigger
    phrase is present.
