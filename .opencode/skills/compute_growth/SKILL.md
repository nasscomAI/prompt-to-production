---
name: compute-growth
description: Takes ward, category, and growth type, returns per-period growth table with formula shown
---

## What I do
- Take ward, category, and growth type (MoM or YoY)
- Compute per-period growth from the dataset
- Show the formula used in every output row
- Flag null rows before computing

## Input
- ward: string
- category: string
- growth_type: "MoM" or "YoY"

## Output
- Per-period growth table with formula shown alongside each result

## Error handling
- If growth_type is not specified, refuse and ask — never guess
- Skip null actual_spend rows with a flag and reason
