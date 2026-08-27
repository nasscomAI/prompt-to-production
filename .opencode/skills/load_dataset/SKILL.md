---
name: load-dataset
description: Reads ward budget CSV, validates columns, reports null count and which rows before returning
---

## What I do
- Load the ward_budget.csv file
- Validate expected columns: period, ward, category, budgeted_amount, actual_spend, notes
- Count and report null actual_spend values with their row details
- Return validated dataset

## Input
- File path: string (path to CSV file)

## Output
- Validated dataset with null row report

## Error handling
- Report column validation errors
- Always report null rows before returning data
