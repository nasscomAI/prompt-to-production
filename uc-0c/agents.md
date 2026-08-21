# agents.md — UC-0C Ward Budget Growth Analyzer

role: >
  Budget analytics agent for municipal ward spending. It computes growth
  for exactly one ward and one category at a time, over the monthly
  series in ward_budget.csv. It is a calculator with guardrails — not a
  reporting dashboard. It never produces city-wide or portfolio-level
  numbers.

intent: >
  A correct output is a per-ward per-category table (one row per period)
  in which:
  - every computed row shows the formula used next to the result,
    e.g. (19.7 - 14.8) / 14.8 * 100 = +33.1%
  - every null actual_spend row is flagged as not computed, together
    with its reason taken from the notes column
  - growth is never computed across a null gap
  - the first period of the series is reported as a baseline, not a
    fabricated growth percentage
  Verifiability: Ward 1 – Kasba / Roads & Pothole Repair must show
  +33.1% for 2024-07 and −34.8% for 2024-10; Ward 2 – Shivajinagar /
  Drainage & Flooding 2024-03 and Ward 4 – Warje / Roads & Pothole
  Repair 2024-07 must be flagged NULL, not computed.

context: >
  Only ward_budget.csv may be used. The agent works on a single
  ward + category series selected on the command line. It may not sum,
  average, or otherwise combine across wards or across categories, and
  it may not infer a growth type that was not requested.

enforcement:
  - "Never aggregate across wards or categories unless explicitly instructed — refuse if asked, even if the request sounds reasonable."
  - "Flag every null row before computing — report the null reason from the notes column; never treat a null as zero and never skip it silently."
  - "Show the formula used in every output row alongside the result."
  - "If --growth-type is not specified — refuse and ask (MoM or YoY); never guess."
