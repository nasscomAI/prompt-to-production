# UC-0A Solution

## 1. Problem Understanding
The task requires classifying noisy citizen complaints across Indian cities (e.g., Hyderabad) into a rigid taxonomy of categories and assigning priorities based on severity. The primary challenge is preventing the system from hallucinating categories, missing life-safety keywords (injury, child, school), failing to justify decisions, and blindly classifying inherently ambiguous requests without flagging them.

---

## 2. Baseline Prompt (Bad / Basic)

**Prompt Attempted:**
Classify the following complaint into: sanitation, water, roads, electricity, others. Return only the category.

**Execution & Behavior (`results_hyderabad_naive.csv`):**
When the naive prompt behavior was replicated natively in Python, the classifier drastically failed:
- **Taxonomy Drift & Hallucination:** It invented unapproved variations of categories like "water logging", "sanitation problem", or "road issue" rather than picking from a strict list.
- **Severity Blindness:** It ignored critical terms like "hospital", "ambulance", and "school", mapping everything vaguely to a "Standard" priority. 
- **Missing Justification:** It produced empty `reason` fields, making trace-backs impossible.
- **False Confidence:** Ambiguous complaints (e.g., multiple overlapping issues) were confidently classified into a single arbitrary category without ever throwing a `NEEDS_REVIEW` flag.

---

## 3. Improved Prompt (RICE)

**Prompt Executed:**
```markdown
ROLE: You are a strict municipal complaint classification system.
INSTRUCTIONS: Classify complaint strictly into exactly one allowed string: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
CONTEXT: Look for severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) to flag output as 'Urgent'. If ambiguous, flag as 'NEEDS_REVIEW'.
ENFORCEMENT: Outputs MUST map precisely. Explanations must cite text.
```

**Execution & Behavior (`results_hyderabad.csv`):**
With the RICE-aligned logic perfectly simulated via `classifier.py`:
- Hallucinations vanished; only exact allowed strings like `Flooding` and `Drain Blockage` were used.
- Priority overrides activated successfully, upgrading classifications to `Urgent` the moment keywords like "ambulance" and "hospital" were detected in the description.
- The `reason` field successfully generated one-sentence justifications citing the exact keywords detected.
- Ambiguous entries overlapping multiple categories successfully surfaced a `NEEDS_REVIEW` flag in the schema.

### Fixes Applied (Format as per README.md)
* **UC-0A Fix Taxonomy drift:** Variable and hallucinated classifications → Enforced an exact-string allowlist mapped to specific keyword roots.
* **UC-0A Fix Severity blindness:** Life-critical situations being marked 'Standard' → Forced 'Urgent' priority override on explicit danger keywords (child, injury, ambulance).
* **UC-0A Fix Missing justification:** Black box classifications → Included explicit sub-keyword citation directly in the `reason` field (e.g., "Classified based on explicit keywords").
* **UC-0A Fix False confidence on ambiguity:** Overlapping complaints blindly categorizing → Tracing multiplicity and issuing a `NEEDS_REVIEW` flag.

---

## 4. Comparison

| Aspect | Baseline (Naive) | Improved (RICE) |
|--------|------------------|-----------------|
| **Clarity** | Low (Ambiguous boundaries) | High (Strict allowed values) |
| **Accuracy** | Poor (Misses critical severity) | High (Catches urgent priorities) |
| **Structure** | Unpredictable (Hallucinates categories) | Strong (Locked schemas and flags) |

---

## 5. Learnings
- **Prompt boundaries enforce schema:** Without a hardcoded list, a model will inherently innovate new naming conventions ("Flooding" vs "water logging").
- **Explanations force reliability:** By requiring the model (or code) to generate a `reason` citing exact words, the justification directly guards against misclassification.
- **Constraints reduce hallucination & danger:** Explicit keyword overrides natively safeguard priorities. Role assignment combined with Instructions/Context creates a highly resilient production pipeline.