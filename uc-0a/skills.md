# Skills
- `classify_complaint`: takes one complaint row in -> outputs category + priority + reason + flag.
- `batch_classify`: reads input CSV, applies classify_complaint per row, writes output CSV gracefully handling nulls and errors.
