---
name: batch-classify
description: Reads input CSV, applies classify_complaint per row, writes output CSV with classifications
---

## What I do
- Read a CSV file containing complaint descriptions
- Apply the classify_complaint skill to each row
- Write an output CSV with category, priority, reason, and flag columns

## Input
- Input CSV path: string
- Output CSV path: string

## Output
- Written output CSV file with classification columns

## Error handling
- Validate that input CSV exists and has required columns
- Skip malformed rows with an error log
