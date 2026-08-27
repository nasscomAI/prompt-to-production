# Agents - UC-0B Summary Generator

## Agent Name
Policy Summary Agent

## Purpose
To generate summaries of policy documents without changing meaning.

## Responsibilities
- Read policy document
- Extract key clauses
- Preserve all important rules
- Generate accurate summary

## Constraints
- Must NOT omit critical clauses
- Must NOT change meaning
- Must include all numbered points

# Skills - UC-0B

## Text Processing
- Read text files
- Split into clauses

## Summarization
- Extract key sentences
- Maintain logical structure

## Validation
- Ensure all clauses are included
- Avoid meaning distortion

## Output Handling
- Write summary to file

import re

# Input & Output
input_file = "../data/policy-documents/policy_hr_leave.txt"
output_file = "summary_hr_leave.txt"

def extract_clauses(text):
    # Split based on numbered clauses (1., 2., etc.)
    clauses = re.split(r'\n?\d+\.\s', text)
    clauses = [c.strip() for c in clauses if c.strip()]
    return clauses

def summarize(clauses):
    summary = []

    for i, clause in enumerate(clauses, 1):
        # Take first sentence to preserve meaning
        sentence = clause.split('.')[0]
        summary.append(f"{i}. {sentence.strip()}.")

    return "\n".join(summary)


# Read file
with open(input_file, "r", encoding="utf-8") as f:
    text = f.read()

# Process
clauses = extract_clauses(text)
summary = summarize(clauses)

# Write output
with open(output_file, "w", encoding="utf-8") as f:
    f.write(summary)

print("Summary generated successfully!")

## Commit Formula
UC-0B Fix clause omission: summaries lost meaning → enforced inclusion of all numbered clauses
```
