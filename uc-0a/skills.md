# UC-0A Complaint Classifier — Skills

## Skills

### 1. Keyword Classification

- **name**: `classify_complaint`
- **description**: Classifies a complaint description into one of five categories using rule-based keyword matching.
- **input**: Complaint text (string), optional location (string)
- **output**: Dict with `category`, `reason`, `confidence`
- **error_handling**: Empty input returns `category: others`, `confidence: low`, `reason: "Empty description"`. Invalid input types return same fallback.

### 2. Batch Processing

- **name**: `batch_classify`
- **description**: Reads CSV, classifies each row, and writes structured output.
- **input**: Input CSV path (str), output path (str)
- **output**: List of classification results, success/fail counts
- **error_handling**: Skip bad rows; log errors; produce partial output. Never crash on malformed rows.

---

## Prompts (for AI-assisted refinement)

**Classification prompt** (when building/refining keyword rules):

> Given complaint: "{description}"
> Classify into one of: sanitation, roads, water, electricity, others.
> Cite the exact words that justify your choice.

---

## Validation Rules

| Rule | Check |
|------|-------|
| Category valid | `category in ["sanitation", "roads", "water", "electricity", "others"]` |
| Reason non-empty | `len(reason) > 0` |
| Confidence valid | `confidence in ["high", "medium", "low"]` |
| Complaint ID present | Output includes original `complaint_id` |

---

## Keyword Mapping (Reference)

| Category | Keywords (case-insensitive) |
|----------|-----------------------------|
| sanitation | garbage, waste, bin, trash, overflow, dump, dead animal, smell, garbage bins, bulk waste, landfill |
| roads | pothole, road, crack, sink, footpath, manhole, tiles, surface, repair |
| water | flood, drain, water, drainage, flooded, blocked drain, stormwater |
| electricity | streetlight, light, power, electrical, flickering, sparking, lights out |
| others | (fallback when no match) |

---

## Example Inputs/Outputs

**Input** (description):
```
Large pothole 60cm wide causing tyre damage. Three vehicles affected this week.
```

**Output**:
```json
{
  "complaint_id": "PM-202401",
  "category": "roads",
  "reason": "pothole",
  "confidence": "high"
}
```

---

**Input** (description):
```
Overflowing garbage bins near vegetable market. Smell affecting shoppers.
```

**Output**:
```json
{
  "complaint_id": "PM-202413",
  "category": "sanitation",
  "reason": "garbage bins, overflow, smell",
  "confidence": "high"
}
```

---

**Input** (description):
```
Wedding venue playing music past midnight on weeknights.
```

**Output**:
```json
{
  "complaint_id": "PM-202418",
  "category": "others",
  "reason": "No matching keywords found",
  "confidence": "low"
}
```
