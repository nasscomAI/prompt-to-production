# skills.md — UC-0A: Complaint Classifier

## Skill: classify_complaint

**Purpose:** Given a complaint text string, return a `category`, `severity`, and a one-line `reason`.

---

## Categories (exactly 8 — use these labels verbatim)

| Category | When to use |
|---|---|
| `ROADS` | Potholes, road damage, broken footpaths, missing manholes, road flooding |
| `SANITATION` | Garbage not collected, open dumping, overflowing bins, drain blockage |
| `WATER` | No water supply, low pressure, contaminated water, pipeline burst/leak |
| `ELECTRICITY` | Power outage, broken streetlight, fallen wire, meter issue |
| `NOISE` | Loud music, construction noise at night, loudspeaker violations |
| `PUBLIC_SAFETY` | Stray animals, unsafe structures, crime hotspot, dangerous open pits |
| `ENVIRONMENT` | Illegal construction, tree cutting, air/water pollution, encroachment |
| `OTHER` | Does not fit any category above |

---

## Severity Levels (exactly 3)

| Severity | Criteria |
|---|---|
| `HIGH` | Risk to human life or urgent public safety. Trigger keywords: injury, accident, child, school, hospital, fire, death, collapsed, electric shock, open wire, contaminated drinking water, sewage overflow near homes |
| `MEDIUM` | Ongoing civic issue causing significant inconvenience but no immediate danger |
| `LOW` | Minor or cosmetic issue; inconvenient but not harmful |

---

## Few-Shot Classification Examples

### Example 1
**Input:** "There is a huge pothole on MG Road near the bus stop. Two bikes skidded last week and one person was injured."  
**Output:**
- category: `ROADS`
- severity: `HIGH`
- reason: Pothole causing accidents and injury reported.

---

### Example 2
**Input:** "The garbage van has not come to our area for 5 days. Waste is piling up on the street."  
**Output:**
- category: `SANITATION`
- severity: `MEDIUM`
- reason: Garbage collection missed for multiple days; no immediate danger.

---

### Example 3
**Input:** "One streetlight near my house has been out for two days."  
**Output:**
- category: `ELECTRICITY`
- severity: `LOW`
- reason: Single streetlight failure; inconvenient but not urgent.

---

### Example 4
**Input:** "There is a live electric wire hanging loose near the government school entrance."  
**Output:**
- category: `PUBLIC_SAFETY`
- severity: `HIGH`
- reason: Exposed live wire near school — immediate danger to children.

---

### Example 5
**Input:** "Water coming from the tap is brownish and smells bad. Children at home are falling sick."  
**Output:**
- category: `WATER`
- severity: `HIGH`
- reason: Contaminated water supply causing illness, children affected.

---

## Enforcement Rules

1. **Severity HIGH must be assigned** when any of these words appear in the complaint: `injury`, `injured`, `accident`, `child`, `children`, `school`, `hospital`, `fire`, `death`, `died`, `collapsed`, `electric shock`, `live wire`, `open wire`, `contaminated`, `sick`, `sewage overflow`.
2. **Category must be one of the 8 listed** — no variations or synonyms.
3. **Reason must be one sentence**, plain English, explaining the classification decision.
