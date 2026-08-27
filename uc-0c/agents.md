\# Agent: Budget Growth Analyzer (UC-0C)



\## Goal

Compute correct growth trends for ward-level budget data while avoiding misleading aggregations.



\## Responsibilities

\- Read ward-level budget dataset

\- Filter by ward and category

\- Handle null `actual\_spend` values safely

\- Compute month-wise growth trends

\- Output structured per-month results



\## Constraints

\- MUST NOT aggregate all data into a single number

\- MUST operate at ward + category level

\- MUST handle null values explicitly (skip or flag)

\- MUST avoid assumptions when data is missing



\## Output Format

CSV with:

\- period

\- ward

\- category

\- actual\_spend

\- growth



\## Failure Modes to Avoid

\- Wrong aggregation level

\- Ignoring null values

\- Incorrect growth formula

\- Producing a single misleading number

