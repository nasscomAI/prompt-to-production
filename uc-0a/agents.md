# UC-0A — Complaint Classifier · agents.md

## Agent Identity
- **Name:** ComplaintClassifierAgent
- **Role:** Classify civic complaints from CSV input into category, subcategory, and severity
- **Owner:** Gaddam Siddharth
- **City:** Hyderabad

---

## Goal
Read complaint text from `test_hyderabad.csv`, classify each row, and write results to `results_hyderabad.csv` with:
- `category` (e.g. Roads, Water, Sanitation, Electricity, Other)
- `subcategory` (specific issue type)
- `severity` (Low / Medium / High / Critical)

---

## Inputs
| Field | Description |
|-------|-------------|
| `complaint_id` | Unique row identifier |
| `complaint_text` | Raw text of the civic complaint |
| `ward` | Ward number or name |

## Outputs
| Field | Description |
|-------|-------------|
| `complaint_id` | Passed through unchanged |
| `category` | Top-level complaint category |
| `subcategory` | Specific issue within category |
| `severity` | Low / Medium / High / Critical |
| `reasoning` | One-line justification for classification |

---

## Reasoning Rules (CRAFT-refined)

### Category Keywords
| Category | Keywords |
|----------|----------|
| Roads | pothole, road, footpath, pavement, crack, broken road, divider |
| Water | water, pipe, leakage, supply, drainage, sewage, flood |
| Sanitation | garbage, waste, trash, dustbin, sweeping, cleanliness, dumping |
| Electricity | light, power, electricity, streetlight, wire, pole, transformer |
| Other | anything that doesn't match above |

### Severity Triggers
| Severity | Trigger Conditions |
|----------|--------------------|
| Critical | injury, accident, hospital, child, school, death, fire, collapse |
| High | no water for 2+ days, road completely blocked, open wire, flooding |
| Medium | intermittent issue, partial service loss, recurring complaint |
| Low | aesthetic issues, minor inconvenience, one-time minor event |

### Enforcement
- Severity MUST be elevated to Critical if any Critical keyword appears — regardless of category
- Default severity is Medium if no strong signal either way
- Never return empty `category` or `severity`

---

## Constraints
- Process every row; do not skip
- Output CSV must have same number of rows as input
- reasoning must be ≤ 20 words
