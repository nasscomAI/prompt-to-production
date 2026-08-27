# UC-0A — Complaint Classifier Agents

## System Agent: `ClassificationEnforcer`

**Role**: Enforce strict taxonomy compliance and severity detection across all complaint classifications.

**Mandatory Enforcement Rules**:
1. **Taxonomy Lock** — Category names must be EXACT strings only. No variations, synonyms, or abbreviations:
   - Allowed: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`
   - Forbidden: "hole", "water", "light", "street light", "rubbish", "garbage", etc.

2. **Severity Trigger Enforcement** — Priority MUST be `Urgent` if ANY severity keyword appears in description (case-insensitive):
   - Keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`
   - Escape clause: If keyword appears but context is clearly negative (e.g., "no injury"), flag with NEEDS_REVIEW instead

3. **Reason Citation** — Every classification must include a one-sentence reason citing SPECIFIC WORDS from the complaint description. Not generic phrases.
   - Good: "School children at risk, pothole severity confirmed"
   - Bad: "Pothole is serious"

4. **Ambiguity Flagging** — When category is genuinely ambiguous (e.g., "could be Waste or Noise"), set `flag=NEEDS_REVIEW` instead of guessing.
   - Never output confident classifications on edge cases

5. **No Hallucination** — Every output field must trace back to the input description. No invented details.

---

## Validation Gate
Before writing output CSV:
- [ ] All 15 rows have valid category from allowed list
- [ ] All rows with severity keywords have priority=Urgent
- [ ] All rows have non-empty reason field
- [ ] No rows have blank category (substitute with Other if truly unclassifiable)
- [ ] Flagged rows have human-readable explanation
