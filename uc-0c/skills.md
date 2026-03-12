# Skills Definition — Citizen Complaint Classification System

> Reusable AI skills powering the complaint classification pipeline. Each skill is self-contained and used by one or more agents.

---

## Skill 1: Text Classification

**Skill Name:** `text_classification`

**Description:**
Classifies free-text complaint descriptions into predefined categories using keyword matching, TF-IDF similarity, or LLM-based classification.

**Input Format:**
```json
{
  "text": "string — raw complaint description",
  "taxonomy": ["Sanitation", "Water Supply", "Electricity", "Roads & Infrastructure",
               "Healthcare", "Education", "Public Safety"]
}
```

**Output Format:**
```json
{
  "category": "Roads & Infrastructure",
  "sub_category": "Pothole",
  "confidence": 0.92,
  "alternative_categories": [{"category": "Public Safety", "confidence": 0.15}]
}
```

**Algorithm / Model Used:**
- **Primary:** Rule-based keyword matching against category trigger lists
- **Secondary:** TF-IDF + Logistic Regression (trained on labelled complaint corpus)
- **Fallback:** LLM zero-shot classification (Gemini / GPT) for low-confidence cases
- **Accuracy Target:** >85% (rule-based), >92% (fine-tuned BERT)

**Example Use Case:**
```
Input:  "Road surface cracked and sinking near utility work done 1 month ago."
Output: { category: "Roads & Infrastructure", sub_category: "Road Damage", confidence: 0.89 }
```

---

## Skill 2: Keyword Extraction

**Skill Name:** `keyword_extraction`

**Description:**
Extracts domain-relevant keywords, severity indicators, and numeric entities from complaint text.

**Input Format:**
```json
{
  "text": "string — complaint description",
  "domain_lexicon": ["pothole", "drain", "garbage", "streetlight", "flooding", "manhole", ...]
}
```

**Output Format:**
```json
{
  "keywords": ["pothole", "tyre damage", "vehicles"],
  "domain_matches": ["pothole"],
  "severity_indicators": ["damage"],
  "numeric_entities": [{"value": "60cm", "context": "width"}, {"value": "3", "context": "vehicles"}]
}
```

**Algorithm / Model Used:**
- **Primary:** Domain lexicon matching with regex patterns
- **Secondary:** RAKE (Rapid Automatic Keyword Extraction) algorithm
- **Numeric extraction:** Regex patterns for measurements, counts, durations

**Example Use Case:**
```
Input:  "Overflowing garbage bins near vegetable market. Smell affecting shoppers."
Output: { keywords: ["garbage", "overflowing", "bins", "smell"],
          domain_matches: ["garbage", "overflowing"],
          severity_indicators: ["overflowing", "affecting"] }
```

---

## Skill 3: Urgency Detection

**Skill Name:** `urgency_detection`

**Description:**
Scans complaint text and metadata to determine urgency. Critical keyword triggers cause immediate escalation; secondary factors adjust the score.

**Input Format:**
```json
{
  "text": "string — complaint description",
  "days_open": 13,
  "category": "Water Supply"
}
```

**Output Format:**
```json
{
  "priority": "URGENT",
  "urgency_score": 9,
  "triggers_matched": [
    {"trigger": "ambulance", "type": "critical_keyword"},
    {"trigger": "lives at risk", "type": "critical_keyword"}
  ],
  "escalation_required": true
}
```

**Algorithm / Model Used:**
- **Primary:** Rule engine with keyword trigger matching
- **Scoring:** Weighted multi-factor algorithm (keywords 40%, SLA 25%, impact 20%, criticality 15%)
- **SLA calculator:** Configurable thresholds per category

**Trigger Rules:**
- `child`, `school`, `injury`, `hospital` → **URGENT**
- `ambulance`, `lives at risk`, `death` → **URGENT**
- `gas leak`, `electrical hazard`, `sparking` → **URGENT**
- `collapse`, `structural`, `crater` → **URGENT**
- `dengue`, `disease`, `epidemic` → **URGENT**
- `days_open > 14` → minimum **HIGH**

**Example Use Case:**
```
Input:  text: "Manhole cover missing. Risk of serious injury to cyclists." | days_open: 14
Output: { priority: "URGENT", urgency_score: 8, triggers: ["injury", "risk"] }
```

---

## Skill 4: Named Entity Recognition

**Skill Name:** `named_entity_recognition`

**Description:**
Extracts structured entities from complaint text: locations, infrastructure, organisations, dates/times, and quantities.

**Input Format:**
```json
{
  "text": "string — complaint description",
  "city_context": "Pune"
}
```

**Output Format:**
```json
{
  "locations": ["Karve Road", "Deccan Gymkhana"],
  "infrastructure": ["pothole"],
  "organisations": [],
  "temporal": ["this week"],
  "quantities": [{"value": "60cm", "unit": "width"}, {"value": "3", "unit": "vehicles"}]
}
```

**Algorithm / Model Used:**
- **Primary:** spaCy NER pipeline with custom city-domain training
- **Fallback:** Regex-based extraction for locations and measurements
- **Location disambiguation:** City-context-aware matching with gazetteer lookups

**Example Use Case:**
```
Input:  "Heritage lamp post knocked over by delivery vehicle near Victoria area."
        city_context: "Kolkata"
Output: { locations: ["Victoria area"], infrastructure: ["lamp post"], temporal: [] }
```

---

## Skill 5: Department Mapping

**Skill Name:** `department_mapping`

**Description:**
Maps classified complaint category to the responsible city department using a configurable lookup table.

**Input Format:**
```json
{
  "category": "Roads & Infrastructure",
  "sub_category": "Pothole",
  "priority": "HIGH",
  "city": "Pune"
}
```

**Output Format:**
```json
{
  "primary_department": "Public Works Department",
  "department_code": "PWD",
  "secondary_department": null,
  "escalation_targets": [],
  "routing_reason": "Category 'Roads & Infrastructure' maps to PWD"
}
```

**Algorithm / Model Used:**
- **Primary:** Lookup table (configurable per city)
- **Cross-department logic:** Rule engine for multi-category complaints
- **Escalation:** Priority-based notification rules

**Mapping Table:**

| Category | Department | Code |
|---|---|---|
| Sanitation | Sanitation Department | SAN |
| Water Supply | Water Authority | WAT |
| Electricity | Electrical Maintenance Division | EMD |
| Roads & Infrastructure | Public Works Department | PWD |
| Healthcare | Public Health Department | PHD |
| Education | Education Department | EDU |
| Public Safety | Police / Emergency Services | PES |
| Uncategorised | General Complaints Cell | GCC |

**Example Use Case:**
```
Input:  category: "Sanitation", priority: "URGENT"
Output: { department: "Sanitation Department", code: "SAN",
          escalation_targets: ["Commissioner's Office"] }
```

---

## Skill 6: Data Validation

**Skill Name:** `data_validation`

**Description:**
Validates incoming complaint data for schema compliance, data types, and business rules before processing.

**Input Format:**
```json
{
  "records": [{"complaint_id": "PM-202401", "date_raised": "2024-06-21", ...}],
  "expected_schema": {
    "complaint_id": "string, required, unique",
    "date_raised": "date (YYYY-MM-DD), required",
    "city": "string, required",
    "ward": "string, required",
    "location": "string, required",
    "description": "string, required, min_length: 5",
    "reported_by": "string, required",
    "days_open": "integer, required, >= 0"
  }
}
```

**Output Format:**
```json
{
  "total_records": 16,
  "valid_records": 16,
  "invalid_records": 0,
  "validation_errors": [],
  "null_report": {"description": 0, "days_open": 0},
  "duplicate_ids": [],
  "schema_compliant": true
}
```

**Algorithm / Model Used:**
- JSON schema validation (jsonschema library)
- Custom business rule engine for field-level checks
- Deduplication using complaint_id hash

**Example Use Case:**
```
Input:  16 records from test_pune.csv
Output: { total: 16, valid: 16, invalid: 0, schema_compliant: true }
```
