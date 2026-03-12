# Classification Logic — Citizen Complaint Classification System

> Rules and logic used for complaint classification, department routing, and priority detection.

---

## 1. Complaint Categories

| # | Category | Description | Example Complaints |
|---|---|---|---|
| 1 | **Sanitation** | Waste, garbage, dead animals, market waste | Overflowing garbage bins, dead animal not removed |
| 2 | **Water Supply** | Pipe issues, flooding, drainage, waterlogging | Drain blocked, underpass flooded, pipe burst |
| 3 | **Electricity** | Streetlights, wiring, substations, sparking | Lights out, flickering, wiring theft, substation tripped |
| 4 | **Roads & Infrastructure** | Potholes, road damage, footpaths, manholes | Road cracked, pothole causing tyre damage, manhole missing |
| 5 | **Healthcare** | Public health risks, disease, contamination | Dengue concern, health risk from waste |
| 6 | **Education** | School-related infrastructure and safety | School area unsafe, educational facility damage |
| 7 | **Public Safety** | Noise, hazards, structural collapse, fire | Music at midnight, gas leak, building collapse |

---

## 2. Keyword Mapping

### Category → Keyword Trigger Lists

**Sanitation:**
```
garbage, waste, rubbish, bins, overflowing, dump, sanitation,
dead animal, smell, odour, sewage, market waste, health risk,
bulk waste, renovation waste, not cleared
```

**Water Supply:**
```
water, pipe, drain, flooding, flooded, waterlog, blocked drain,
underpass, stormwater, rain, submerge, knee-deep, stranded,
burst pipe, no water, low pressure, contamination, mosquito
```

**Electricity:**
```
streetlight, light, dark, electrical, wiring, sparking, substation,
unlit, flickering, tripped, power, outage, electrocution, wire theft
```

**Roads & Infrastructure:**
```
pothole, road, tarmac, surface, crack, sinking, collapsed, crater,
footpath, tiles, paving, highway, manhole, bridge, underpass,
road divider, lane closure, subsidence
```

**Healthcare:**
```
dengue, malaria, disease, epidemic, health, hospital, medical,
contamination, breeding, infection, health risk
```

**Education:**
```
school, college, university, education, students, campus, classroom,
playground, school bus, children safety
```

**Public Safety:**
```
noise, music, midnight, construction, drilling, amplifier, nuisance,
gas leak, fire, collapse, structural, explosion, hazard, unsafe,
danger, risk, accident, criminal
```

### Classification Algorithm

```python
def classify_complaint(description, taxonomy):
    tokens = tokenize_and_lowercase(description)
    scores = {}

    for category in taxonomy:
        triggers = get_triggers(category)
        match_count = sum(1 for t in triggers if t in tokens)
        scores[category] = match_count / len(triggers)

    best = max(scores, key=scores.get)

    if scores[best] >= 0.1:
        return {"category": best, "confidence": min(scores[best] * 3, 1.0)}
    else:
        return {"category": "Uncategorised", "confidence": 0.0, "flag": "NEEDS_REVIEW"}
```

---

## 3. Department Routing Rules

### Primary Routing Table

| Complaint Category | Routed To | Department Code |
|---|---|---|
| Sanitation | Sanitation Department | SAN |
| Water Supply | Water Authority | WAT |
| Electricity | Electrical Maintenance Division | EMD |
| Roads & Infrastructure | Public Works Department | PWD |
| Healthcare | Public Health Department | PHD |
| Education | Education Department | EDU |
| Public Safety | Police / Emergency Services | PES |
| Uncategorised | General Complaints Cell | GCC |

### Cross-Department Routing Rules

| Condition | Primary | Secondary |
|---|---|---|
| Flooding + Road damage in description | PWD | WAT |
| Waste + Health/disease mention | SAN | PHD |
| Electrical hazard + Public space | EMD | PES |
| School + Infrastructure damage | EDU | PWD |
| Heritage + Infrastructure | PWD | Heritage Conservation Cell |

### Escalation Rules

| Condition | Action |
|---|---|
| Priority = URGENT | Notify Municipal Commissioner's Office |
| Priority = HIGH + days_open > 14 | Notify Ward Commissioner |
| Priority = URGENT + days_open > 7 | Emergency Cell activation |
| Any complaint > 21 days open | Auto-escalate to Commissioner |

### Routing Decision Tree

```
START
  │
  ├── Category identified?
  │   ├── YES → Look up Department Mapping Table
  │   │   ├── Cross-department triggers present?
  │   │   │   ├── YES → Assign primary + secondary department
  │   │   │   └── NO → Assign primary department only
  │   │   │
  │   │   ├── Priority = URGENT?
  │   │   │   ├── YES → Add Commissioner to notification list
  │   │   │   └── NO → Standard routing
  │   │   │
  │   │   └── OUTPUT: department, code, routing_reason
  │   │
  │   └── NO (Uncategorised)
  │       └── Route to General Complaints Cell (GCC)
  │           └── Flag for manual triage within 2 hours
  │
  END
```

---

## 4. Priority Detection Rules

### Priority Levels

| Level | Symbol | Response Target | Description |
|---|---|---|---|
| **URGENT** | 🔴 | < 4 hours | Immediate threat — life, safety, or critical infrastructure |
| **HIGH** | 🟠 | < 24 hours | Significant impact, SLA breach risk, hazardous conditions |
| **MEDIUM** | 🟡 | < 72 hours | Standard complaint affecting daily life, no immediate danger |
| **LOW** | 🟢 | < 7 days | Cosmetic, minor inconvenience, suggestion |

### Critical Keyword Triggers (→ AUTO URGENT)

```
URGENT_TRIGGERS = {
    # Child / School Safety
    "child", "children", "school", "minor", "student",

    # Medical Emergency
    "injury", "injured", "hospital", "hospitalised", "ambulance",

    # Life Threat
    "lives at risk", "death", "fatal", "life-threatening",

    # Hazardous Material
    "gas leak", "gas smell", "chemical",

    # Electrical Danger
    "electrical hazard", "sparking", "electrocution",

    # Public Health Emergency
    "dengue", "malaria", "disease", "epidemic",

    # Structural Failure
    "collapse", "collapsed", "structural", "crater",

    # Fire
    "fire", "burning", "smoke"
}
```

### Scoring Algorithm

```python
def calculate_priority(description, days_open, category):
    # Factor 1: Critical keyword check (immediate override)
    for keyword in URGENT_TRIGGERS:
        if keyword in description.lower():
            return {"priority": "URGENT", "score": 9, "escalation": True}

    score = 0

    # Factor 2: SLA / days_open (25% weight)
    if days_open > 21:   score += 2.5
    elif days_open > 14: score += 2.0
    elif days_open > 7:  score += 1.5
    elif days_open > 3:  score += 0.5

    # Factor 3: Impact scope (20% weight)
    if has_public_impact(description):      score += 2.0
    elif has_multiple_people(description):  score += 1.0
    else:                                   score += 0.5

    # Factor 4: Category criticality (15% weight)
    critical_cats = ["Roads & Infrastructure", "Water Supply", "Electricity"]
    if category in critical_cats: score += 1.5
    else:                         score += 0.5

    # Map score to priority
    if score >= 5.5: return {"priority": "HIGH"}
    elif score >= 3:  return {"priority": "MEDIUM"}
    else:             return {"priority": "LOW"}
```

### SLA Thresholds per Category

| Category | URGENT SLA | Standard SLA | Breach Escalation |
|---|---|---|---|
| Roads & Infrastructure | 4 hours | 7 days | Ward Commissioner |
| Water Supply | 2 hours | 5 days | Emergency Cell |
| Sanitation | 12 hours | 3 days | Zonal Officer |
| Electricity | 4 hours | 5 days | EMD Head |
| Healthcare | 2 hours | 3 days | Health Officer |
| Education | 24 hours | 7 days | Education Officer |
| Public Safety | 1 hour | 3 days | Police Control Room |

---

## 5. Real-World Examples from Dataset

| ID | Description (Abridged) | Category | Priority | Department | Trigger |
|---|---|---|---|---|---|
| PM-202402 | Deep pothole. School children at risk. | Roads & Infrastructure | **URGENT** | PWD | "school", "children" |
| GH-202401 | Underpass flooded. Ambulance diverted. Lives at risk. | Water Supply | **URGENT** | WAT | "ambulance", "lives at risk" |
| GH-202411 | Pothole swallowed motorcycle wheel. Rider hospitalised. | Roads & Infrastructure | **URGENT** | PWD | "hospitalised" |
| AM-202407 | Broken bench. Child injured last week. | Public Safety | **URGENT** | PES | "child", "injured" |
| KM-202430 | Road subsided near gas pipeline. Gas leak smell. | Public Safety | **URGENT** | PES + PWD | "gas leak" |
| PM-202411 | Streetlight sparking. Electrical hazard. | Electricity | **URGENT** | EMD | "sparking", "electrical hazard" |
| GH-202407 | Drain blocked. Mosquito breeding. Dengue concern. | Healthcare | **URGENT** | PHD + WAT | "dengue" |
| PM-202413 | Garbage bins overflowing near market. Smell. | Sanitation | MEDIUM | SAN | — |
| PM-202418 | Music past midnight on weeknights. | Public Safety | LOW | PES | — |
| AM-202410 | Pothole on highway causing lane closure. | Roads & Infrastructure | HIGH | PWD | days_open: 4 |
