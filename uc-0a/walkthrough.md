# Walkthrough - UC-0A Complaint Classifier

I have updated the `classifier.py` script and populated `agents.md` and `skills.md` to meet the requirements for the UC-0A Complaint Classifier.

## Changes Made
- **[agents.md](file:///c:/Users/Vineel%20Kumar/Videos/anil/Nasscom/prompt-to-production/uc-0a/agents.md)**: Updated with the specific role, intent, context, and enforcement rules for classifying citizen complaints.
- **[skills.md](file:///c:/Users/Vineel%20Kumar/Videos/anil/Nasscom/prompt-to-production/uc-0a/skills.md)**: Defined the `classify_complaint` and `batch_classify` skills.
- **[classifier.py](file:///c:/Users/Vineel%20Kumar/Videos/anil/Nasscom/prompt-to-production/uc-0a/classifier.py)**: Implemented the classification logic using a prioritized keyword matching system.

## Verification Results
I ran the classifier on the Pune test data (`test_pune.csv`). The results were written to `results_pune.csv`.

### Sample Output Analysis
| ID | Description Snippet | Category | Priority | Reason |
|---|---|---|---|---|
| PM-202402 | ...School children at risk... | Pothole | Urgent | Cites 'pothole, child' |
| PM-202411 | ...Electrical hazard reported... | Streetlight | Urgent | Cites 'hazard, light' |
| PM-202430 | ...Heritage street, lights out... | Heritage Damage | Standard | Cites 'heritage' |
| PM-202420 | ...Risk of serious injury... | Road Damage | Urgent | Cites 'injury, manhole' |

### Performance on Edge Cases
- **Priority Overlap**: Correctly identifies 'Urgent' even when multiple categories match.
- **Category Precedence**: 'Heritage Damage' and 'Drain Blockage' are prioritized over general 'Streetlight' or 'Flooding' when relevant keywords are present.
- **Empty/Ambiguous Rows**: Genuinely ambiguous or empty descriptions are flagged with `NEEDS_REVIEW`.

## How to Run
```bash
python classifier.py --input ../data/city-test-files/test_pune.csv --output results_pune.csv
```
