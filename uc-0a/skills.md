# UC-0A — Skills

## classify_complaint
Input: one complaint row (description text)
Output: category, priority, reason, flag
Rules: enforce allowed categories, severity keywords, reason citation

## batch_classify
Input: CSV file path
Output: CSV file with category, priority, reason, flag columns added
Process: applies classify_complaint to every row
