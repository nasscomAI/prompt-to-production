# UC-0B Skills

## retrieve_policy

Load the HR leave policy text file and return its numbered sections in structured form.

Preserve:
- Section numbers
- Original meaning
- Original conditions
- Important dates and time limits
- Approval requirements

Do not add information that is not present in the source.

## summarize_policy

Create a compliant summary from the retrieved policy.

Rules:
1. Include every required numbered clause.
2. Preserve all conditions in each clause.
3. Preserve all required approvers.
4. Preserve dates and time limits.
5. Preserve binding obligations.
6. Do not add information from outside the source.
7. Include the original clause number for every summary point.
8. If summarization could change the meaning, quote the source text and flag it for review.