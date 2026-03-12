# AI Agents Architecture — Citizen Complaint Classification System

## 1. System Overview

The Complaint Classification System operates through a **5-agent modular pipeline** that ingests raw citizen complaint data, applies NLP-based analysis, detects urgency, routes to appropriate departments, and generates actionable reports.

**Design Principles:**
- **Stateless Agents** — each agent processes input independently, enabling horizontal scaling
- **Pipeline Architecture** — agents execute sequentially; each agent enriches the complaint record
- **Fail-Safe Defaults** — ambiguous complaints are flagged for human review, never silently routed
- **Audit Trail** — every agent logs its decision rationale for transparency

**Supported Data Sources:**
- CSV files from `city-test-files/` directory (current)
- REST API ingestion (planned)
- Email / WhatsApp / SMS intake (planned)

**Complaint Categories Supported:**

| # | Category | Department |
|---|---|---|
| 1 | Sanitation | Sanitation Department |
| 2 | Water Supply | Water Authority |
| 3 | Electricity | Electrical Maintenance Division |
| 4 | Roads & Infrastructure | Public Works Department |
| 5 | Healthcare | Public Health Department |
| 6 | Education | Education Department |
| 7 | Public Safety | Police / Emergency Services |

---

## 2. Agent Descriptions

---

### Agent 1: Data Ingestion Agent

**Agent Name:** `data_ingestion_agent`

**Role:**
First entry point in the pipeline. Reads complaint files from `city-test-files/`, parses CSV structure, validates schema, and outputs clean structured records for downstream agents.

**Inputs:**
- Directory path to complaint files (e.g., `data/city-test-files/`)
- Expected schema: `complaint_id, date_raised, city, ward, location, description, reported_by, days_open`

**Outputs:**
- List of validated complaint records (JSON objects)
- Data quality report (row count, null fields, duplicate IDs, schema violations)
- Rejected records list with rejection reasons

**Processing Steps:**
1. Scan target directory for `.csv` files
2. Parse each file using Python `csv` / `pandas`
3. Validate column headers against expected schema
4. For each row: check for nulls, validate data types, ensure unique complaint_id
5. Output validated records + quality report

**Tools / Models Used:**
- Python `csv` module / `pandas` for parsing
- JSON schema validator for structure checks
- File system I/O for directory scanning

**Example Workflow:**
```
1. Scan directory → find test_pune.csv, test_hyderabad.csv, test_kolkata.csv, test_ahmedabad.csv
2. Parse test_pune.csv → 16 rows, 8 columns → schema valid ✓
3. Validate each row:
   - PM-202401: all fields present ✓, days_open=4 (integer) ✓
   - PM-202402: all fields present ✓, days_open=12 (integer) ✓
   ...
4. Output: 64 validated records across 4 files, 0 rejected, 0 nulls in description
```

---

### Agent 2: Complaint Understanding Agent

**Agent Name:** `complaint_understanding_agent`

**Role:**
Core NLP agent. Processes each complaint's `description` to extract keywords, named entities, and classify the complaint into a category. Uses both rule-based keyword matching and NLP model inference.

**Inputs:**
- Validated complaint record (from Data Ingestion Agent)
- Category taxonomy with keyword triggers
- Domain lexicon for city complaints

**Outputs:**
- `category`: Primary complaint category (e.g., "Sanitation", "Roads & Infrastructure")
- `sub_category`: Specific issue type (e.g., "Pothole", "Garbage Overflow")
- `keywords`: Extracted domain-relevant keywords
- `entities`: Named entities (locations, organisations, infrastructure)
- `intent`: Citizen intent (e.g., "repair_request", "safety_alert", "nuisance_report")
- `confidence_score`: 0.0–1.0 classification confidence

**Processing Steps:**
1. Tokenise and lowercase the complaint description
2. Extract keywords using domain lexicon matching
3. Run Named Entity Recognition — extract locations, quantities, infrastructure
4. Match keywords against category trigger lists → compute match scores
5. Select highest-scoring category; if confidence < 0.3 → flag as "Uncategorised"
6. Determine citizen intent from verb/noun patterns

**Tools / Models Used:**
- Regex-based keyword matcher (rule engine)
- spaCy / NLTK for tokenisation and NER
- TF-IDF vectoriser for category similarity scoring
- LLM fallback (Gemini / GPT) for ambiguous descriptions

**Example Workflow:**
```
Input:  "Large pothole 60cm wide causing tyre damage. Three vehicles affected this week."

Step 1: Tokens → ["large", "pothole", "60cm", "wide", "tyre", "damage", "vehicles"]
Step 2: Domain matches → "pothole" ∈ Roads & Infrastructure triggers
Step 3: NER → size: "60cm", affected: "3 vehicles"
Step 4: Score → Roads & Infrastructure: 0.92, Public Safety: 0.15
Step 5: Category = "Roads & Infrastructure", confidence = 0.92
Step 6: Intent = "repair_request"

Output: {
  category: "Roads & Infrastructure",
  sub_category: "Pothole",
  keywords: ["pothole", "tyre damage", "vehicles"],
  entities: {size: "60cm", count: "3 vehicles"},
  intent: "repair_request",
  confidence: 0.92
}
```

---

### Agent 3: Priority Detection Agent

**Agent Name:** `priority_detection_agent`

**Role:**
Determines complaint urgency using keyword triggers, SLA analysis (`days_open`), and contextual severity indicators. Assigns a priority level and escalation flag.

**Inputs:**
- Classified complaint record (from Complaint Understanding Agent)
- `days_open` from original data
- Priority trigger ruleset

**Outputs:**
- `priority`: One of `URGENT`, `HIGH`, `MEDIUM`, `LOW`
- `urgency_score`: Numeric score 1–10
- `escalation_flag`: Boolean
- `trigger_reasons`: List of matched rules
- `sla_status`: "Within SLA" / "SLA Breached" / "SLA At Risk"

**Processing Steps:**
1. Scan description for critical keyword triggers
2. If ANY critical keyword found → immediately set priority = `URGENT`
3. Evaluate `days_open` against SLA thresholds
4. Compute weighted urgency score from 4 factors
5. Map score to priority level
6. Set escalation flag if Critical/Urgent

**Urgency Trigger Rules:**

| Trigger Keywords | Priority |
|---|---|
| child, school, children, minor | → **URGENT** |
| injury, injured, hospital, hospitalised | → **URGENT** |
| ambulance, lives at risk, death, fatal | → **URGENT** |
| gas leak, electrical hazard, sparking, fire | → **URGENT** |
| dengue, disease, epidemic, health risk | → **URGENT** |
| collapse, collapsed, structural, crater | → **URGENT** |

| SLA Rule | Priority |
|---|---|
| days_open > 14 | → Minimum HIGH |
| days_open > 7 AND safety-related category | → URGENT |
| days_open > 21 | → Auto-escalate to Commissioner |

**Tools / Models Used:**
- Rule engine for keyword trigger matching
- Weighted scoring algorithm (4-factor: keywords 40%, SLA 25%, impact 20%, criticality 15%)
- SLA calculator

**Example Workflow:**
```
Input:  GH-202401 — "Underpass flooded. Ambulance diverted. Lives at risk."
        days_open: 13, category: "Water Supply"

Step 1: Keyword scan → "ambulance" ✓, "lives at risk" ✓
Step 2: CRITICAL triggers matched → priority = URGENT (immediate)
Step 3: days_open 13 → HIGH threshold
Step 4: Score = (40×1.0)+(25×0.8)+(20×1.0)+(15×0.9) = 93.5 → urgency: 9
Step 5: priority = "URGENT"
Step 6: escalation_flag = true

Output: { priority: "URGENT", urgency_score: 9, escalation: true,
          triggers: ["ambulance", "lives_at_risk"] }
```

---

### Agent 4: Department Routing Agent

**Agent Name:** `department_routing_agent`

**Role:**
Maps each classified, prioritised complaint to the correct city department. Handles cross-department routing and escalation notifications.

**Inputs:**
- Classified complaint with category (from Complaint Understanding Agent)
- Priority level (from Priority Detection Agent)
- City and ward information

**Outputs:**
- `department`: Target department name
- `department_code`: Standardised identifier
- `secondary_department`: For cross-cutting issues
- `routing_confidence`: 0.0–1.0
- `routing_reason`: Explanation of mapping decision

**Processing Steps:**
1. Lookup category in department mapping table
2. Check for cross-department triggers (e.g., flooding + road damage)
3. If priority is URGENT → add Commissioner's Office to notifications
4. If category is "Uncategorised" → route to General Complaints Cell
5. Output routing decision with reason

**Department Mapping:**

| Complaint Category | Department | Code |
|---|---|---|
| Sanitation | Sanitation Department | SAN |
| Water Supply | Water Authority | WAT |
| Electricity | Electrical Maintenance Division | EMD |
| Roads & Infrastructure | Public Works Department | PWD |
| Healthcare | Public Health Department | PHD |
| Education | Education Department | EDU |
| Public Safety | Police / Emergency Services | PES |
| Uncategorised | General Complaints Cell | GCC |

**Tools / Models Used:**
- Department mapping lookup table (configurable per city)
- Rule engine for multi-department routing
- Notification service for escalations

**Example Workflow:**
```
Input:  category: "Sanitation", sub: "Garbage Overflow", priority: "MEDIUM"
        city: "Pune", ward: "Ward 1 – Kasba"

Step 1: Lookup "Sanitation" → Sanitation Department (SAN) ✓
Step 2: No cross-department triggers
Step 3: Priority MEDIUM → standard routing (no commissioner)
Step 4: Category is valid → bypass GCC

Output: { department: "Sanitation Department", code: "SAN",
          secondary: null, confidence: 0.98,
          reason: "Category 'Sanitation' directly maps to SAN" }
```

---

### Agent 5: Reporting Agent

**Agent Name:** `reporting_agent`

**Role:**
Aggregates results from all upstream agents and generates summary reports, analytics, and exportable outputs. Provides insights on complaint patterns, department workload, and SLA compliance.

**Inputs:**
- All processed complaint records with category, priority, department metadata
- Optional: date range filter, city/ward filter

**Outputs:**
- Classification summary (counts by category, priority, department)
- City-level breakdown
- SLA compliance report
- Trend analysis
- Escalation report (all URGENT complaints)
- Export formats: CSV, JSON, Markdown

**Processing Steps:**
1. Aggregate complaint records by category, priority, department
2. Compute SLA compliance rates per department
3. Identify trends (volume over time, emerging categories)
4. Flag departments with >30% SLA breach rate
5. Generate formatted reports in requested format

**Tools / Models Used:**
- pandas for aggregation and pivoting
- matplotlib / Plotly for chart generation
- Jinja2 for report templating
- CSV / JSON exporters

**Example Workflow:**
```
Input: 64 processed complaints, no filters

Output:
  Category Breakdown:
    Roads & Infrastructure: 18 (28%) | Sanitation: 12 (19%)
    Water Supply: 10 (16%)          | Electricity: 8 (13%)
    Public Safety: 6 (9%)           | Healthcare: 5 (8%)
    Education: 3 (5%)               | Uncategorised: 2 (3%)

  Priority Distribution:
    URGENT: 8 | HIGH: 15 | MEDIUM: 24 | LOW: 17

  SLA Breach Rate: 34% (22 complaints with days_open > 14)
```

---

## 3. Agent Workflow Diagram

```
                         ┌─────────────────────┐
                         │    CSV Files         │
                         │  (city-test-files/)  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   AGENT 1: Data Ingestion     │
                    │   • Parse CSV files            │
                    │   • Validate schema            │
                    │   • Output clean records       │
                    └───────────────┬───────────────┘
                                    │
                         Validated Records (JSON)
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   AGENT 2: Complaint           │
                    │   Understanding                │
                    │   • NLP text analysis          │
                    │   • Keyword extraction         │
                    │   • Category classification    │
                    └───────────────┬───────────────┘
                                    │
                       Classified Records + Keywords
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   AGENT 3: Priority Detection │
                    │   • Keyword trigger scan       │
                    │   • SLA analysis               │
                    │   • Urgency scoring            │
                    └───────────────┬───────────────┘
                                    │
                      Prioritised Records + Scores
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   AGENT 4: Dept. Routing      │
                    │   • Department mapping         │
                    │   • Cross-dept detection       │
                    │   • Escalation notifications   │
                    └───────────────┬───────────────┘
                                    │
                        Routed Records + Dept Info
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   AGENT 5: Reporting           │
                    │   • Aggregation & analytics    │
                    │   • SLA compliance reports      │
                    │   • CSV / JSON export           │
                    └───────────────────────────────┘
```

---

## 4. Data Flow Between Agents

| Stage | Source Agent | Data Passed | Target Agent |
|---|---|---|---|
| 1 → 2 | Data Ingestion | Validated complaint records (JSON array) with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open | Complaint Understanding |
| 2 → 3 | Complaint Understanding | Enriched records with: category, sub_category, keywords, entities, intent, confidence_score | Priority Detection |
| 3 → 4 | Priority Detection | Records with added: priority (URGENT/HIGH/MEDIUM/LOW), urgency_score, escalation_flag, trigger_reasons, sla_status | Department Routing |
| 4 → 5 | Department Routing | Fully processed records with: department, department_code, secondary_department, routing_reason | Reporting |

**Record Schema Evolution:**

```json
// After Agent 1 (Data Ingestion):
{
  "complaint_id": "PM-202401",
  "date_raised": "2024-06-21",
  "city": "Pune",
  "ward": "Ward 4 – Warje",
  "location": "Karve Road near Deccan Gymkhana",
  "description": "Large pothole 60cm wide causing tyre damage.",
  "reported_by": "Citizen Portal",
  "days_open": 4
}

// After Agent 2 (Complaint Understanding) — fields added:
{
  ...previous fields,
  "category": "Roads & Infrastructure",
  "sub_category": "Pothole",
  "keywords": ["pothole", "tyre damage"],
  "entities": {"size": "60cm"},
  "intent": "repair_request",
  "confidence": 0.92
}

// After Agent 3 (Priority Detection) — fields added:
{
  ...previous fields,
  "priority": "MEDIUM",
  "urgency_score": 4,
  "escalation_flag": false,
  "trigger_reasons": [],
  "sla_status": "Within SLA"
}

// After Agent 4 (Department Routing) — fields added:
{
  ...previous fields,
  "department": "Public Works Department",
  "department_code": "PWD",
  "secondary_department": null,
  "routing_reason": "Category 'Roads & Infrastructure' maps to PWD"
}
```

---

## 5. Enforcement Rules

1. Never aggregate across cities unless explicitly instructed — refuse if asked
2. Flag every null/empty description before processing — reject the record
3. Log the classification rationale for every complaint
4. If urgency cannot be determined — default to `MEDIUM`, never guess `URGENT`
5. Critical priority complaints with escalation flag MUST notify Commissioner's Office
6. All rejected/uncategorised complaints must be routed to General Complaints Cell
