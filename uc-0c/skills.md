# Skills: Anti-Silent Aggregation

## Triggers
- Any request to sum, group, or aggregate financial data.

## Core Constraint & Extraction Rules
- **CRITICAL RULE:** Prevent silent data aggregation loss by enforcing a strict "per-ward, per-category" scope.
- Do not collapse distinct categories together under generic labels.
- Output must explicitly preserve the granularity of Ward and Category combinations.