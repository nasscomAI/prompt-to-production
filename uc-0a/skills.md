name: classify\_complaint

description: Classifies a single complaint into category, priority, reason, and flag

input:

&#x20; type: string

&#x20; format: complaint description

output:

&#x20; type: object

&#x20; fields:

&#x20;   category: one of allowed categories

&#x20;   priority: Urgent | Standard | Low

&#x20;   reason: one sentence referencing complaint text

&#x20;   flag: NEEDS\_REVIEW or blank

error\_handling:

&#x20; If complaint is ambiguous, assign best possible category and set flag to NEEDS\_REVIEW

&#x20; If severity keywords present, always set priority to Urgent



\---

name: batch\_classify

description: Processes CSV file and applies classification to each complaint

input:

&#x20; type: file

&#x20; format: CSV input file

output:

&#x20; type: file

&#x20; format: CSV output file with classification fields

error\_handling:

&#x20; If file not found, return error

&#x20; If rows missing data, skip with warning

