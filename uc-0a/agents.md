# UC-0A — Agents

## 1. Baseline Prompt

Classify the complaint into:
- sanitation
- water
- roads
- electricity
- others

Complaint: {input}

Return only category.

---

## Baseline Output Examples

Input: Garbage not collected  
Output: sanitation  

Input: Water not coming  
Output: water  

---

## Issues with Baseline

- No strict rules
- Can be inconsistent
- No handling of unclear inputs
- No priority understanding

---

## 2. Improved Prompt (RICE)

ROLE:
You are a strict municipal complaint classification system.

INSTRUCTIONS:
Classify complaint into exactly one:
- sanitation
- water
- roads
- electricity
- others

CONTEXT:
Complaints may be vague. Choose most critical issue.

EXAMPLES:
Garbage not collected → sanitation  
Water leakage → water  
Potholes on road → roads  
Power cut → electricity  
Noise issue → others  

ENFORCEMENT:
- Only one category
- No explanation
- If unclear → others

INPUT:
{complaint}

OUTPUT:
<category>

---

## Improved Output Examples

Input: Garbage not collected  
Output: sanitation  

Input: Multiple issues but major is water  
Output: water  

---

## Improvements

- Structured output
- Consistent classification
- Handles ambiguity
- Enforced rules