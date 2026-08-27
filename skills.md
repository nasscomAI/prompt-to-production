# UC-0A — Complaint Classifier · skills.md

## Skill 1 — Keyword-Based Category Routing

**What it does:** Maps complaint text to a department using curated keyword lists.

**Keyword Map:**
| Department   | Keywords (case-insensitive)                                              |
|-------------|--------------------------------------------------------------------------|
| Roads        | road, pothole, footpath, pavement, traffic, signal, divider, street      |
| Water        | water, pipe, leak, supply, drainage, sewage, overflow, tap, borewell     |
| Sanitation   | garbage, waste, dustbin, litter, sweeping, trash, dump, cleaning         |
| Electricity  | power, electricity, light, streetlight, wire, transformer, outage, shock |
| Parks        | park, garden, tree, playground, bench, grass, footpath (green area)      |
| Health       | hospital, disease, mosquito, stagnant, rats, hygiene, smell, epidemic    |
| Other        | (fallback when no keywords match)                                         |

**Logic:** Scan complaint text for each keyword group in order. First match wins. If zero matches → `Other`.

---

## Skill 2 — Severity Escalation Detector

**What it does:** Upgrades any classification to `High` if safety-critical terms are present.

**High-severity trigger words:**
```
injury, injured, accident, child, children, school, hospital, fire,
flood, collapse, danger, dangerous, emergency, death, dead, unsafe, bleeding
```

**Rules:**
- If **any** trigger word is found → severity = `High` (overrides all other logic)
- If no trigger found → proceed to Skill 3

---

## Skill 3 — Baseline Severity Scorer

**What it does:** Assigns `Medium` or `Low` when no High-triggers are present.

**Scoring heuristics:**
| Signal                                        | Severity |
|-----------------------------------------------|----------|
| Complaint mentions duration > 3 days          | Medium   |
| Complaint mentions multiple households/area   | Medium   |
| Single household, short-term inconvenience    | Low      |
| No duration or scale mentioned                | Low      |

---

## Skill 4 — Suggested Action Generator

**What it does:** Produces a one-line, department-specific action for field teams.

**Templates by category:**
- **Roads:** `Dispatch [repair crew / inspection team] to [location hint] [urgency phrase]`
- **Water:** `Send plumbing team to inspect [pipe/supply/drainage] issue at reported location`
- **Sanitation:** `Schedule emergency / routine garbage pickup at reported location`
- **Electricity:** `Alert DISCOM for [outage / wire fault / streetlight] repair at reported site`
- **Parks:** `Assign parks maintenance crew to address [tree / bench / grass] issue`
- **Health:** `Notify health inspectors; arrange fogging / pest control at reported site`
- **Other:** `Log complaint and assign duty officer for on-ground assessment`

**Rule:** Always include the implied urgency from severity — High → "immediately", Medium → "within 24 hours", Low → "at next scheduled visit".

---

## Skill 5 — CSV Row Emitter

**What it does:** Formats and writes the final output row safely.

**Rules:**
- Wrap fields containing commas in double-quotes
- No trailing spaces
- Encoding: UTF-8
- One row per complaint; preserve original `complaint_id` column
