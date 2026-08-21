# UC-0C Budget Growth Analysis Agents

## Agent 1 — Data Filtering Agent
Filters dataset by ward and category.

Rules:
- Only one ward allowed
- No multi-ward aggregation

## Agent 2 — Growth Calculation Agent
Calculates month-over-month growth.

Formula:
(Current − Previous) / Previous

## Agent 3 — Data Quality Agent
Detects null values.

Responsibilities:
- Flag rows with missing data
- Skip growth calculation for null entries