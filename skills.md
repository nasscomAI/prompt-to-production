# Skills Definition — UC-0C: Number That Looks Right

## Skill: CSV Ingestion
Read ward_budget.csv using Python's standard csv module. Validate that required
columns (ward, category, amount, total) are present before processing.

## Skill: Scoped Aggregation
Group rows strictly by (ward, category) pairs. Sum the `amount` column within
each group. Never aggregate across ward or category boundaries.

## Skill: Mismatch Detection
Compare each group's computed sum against the recorded `total` value.
Flag as MISMATCH if they differ by more than 0.01 (floating point tolerance).
Flag as OK otherwise.

## Skill: Audit Report Generation
Write growth_output.csv with columns:
ward, category, computed_total, recorded_total, status
Status values: OK or MISMATCH.

## Skill: Silent Error Prevention
Never silently pass a row. Every (ward, category) group must appear in output
with an explicit status — no skipping, no rounding without logging.
