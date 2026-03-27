# Skills

## classify_complaint
Input: One complaint description.

Output:
- category
- priority
- reason
- flag

Logic:
Uses keyword matching to classify complaint category and detect severity keywords for urgent priority. If no category keyword is found, the complaint is marked as "Other" and flagged for review.

## batch_classify
Reads input CSV, applies classify_complaint to each complaint row, and writes the classified results to an output CSV file.
