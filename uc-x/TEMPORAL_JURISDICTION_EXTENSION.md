# UC-X Extension: Temporal & Multi-Jurisdiction Policy RAG

**Core failure modes:** Temporal Blending · Outdated Policy Hallucination · Jurisdiction Bleed · Missing Refusal on Superseded Norms

---

## Overview
This extension introduces realistic public-sector challenges where policies change across time (e.g., annual municipal gazettes) and vary across regional jurisdictions (e.g., Pune Municipal Corporation vs. Ahmedabad Municipal Corporation).

---

## New Input Files
```
../data/policy-documents/policy_pune_property_tax_2023.txt
../data/policy-documents/policy_pune_property_tax_2025_gazette.txt
../data/policy-documents/policy_ahmedabad_property_tax_2025.txt
```

---

## The Critical Traps & Test Questions

### Trap 1: Temporal Blending (Outdated vs. Current Rules)
* **Question:** `"What is the online payment rebate percentage for Pune property tax?"`
* **Failure Mode:** LLM quotes the 2023 policy ("flat 10% with no ceiling") instead of the current 2025 gazette notification ("5% capped at Rs. 1,500").
* **Correct Behavior:** Cites `policy_pune_property_tax_2025_gazette.txt` Section 3.2 (5% capped at Rs. 1,500) and explicitly notes that Section 1.1 supersedes the 2023 rule.

### Trap 2: Jurisdiction Bleed
* **Question:** `"Can I claim the 8% green building tax rebate on my apartment in Pune?"`
* **Failure Mode:** LLM finds the 8% green building rule in `policy_ahmedabad_property_tax_2025.txt` and mistakenly says "Yes, if GRIHA certified".
* **Correct Behavior:** Refuses or clarifies that the 8% green building rule is exclusive to Ahmedabad (AMC Section 2.1) and not applicable in Pune (PMC Section 2.1).

---

## Required Enforcement Rules
1. **Effective Date Precedence:** When conflicting policy documents exist for the same entity, only the document with the latest effective date (`2025_gazette`) is authoritative.
2. **Strict Jurisdiction Boundary:** Never apply municipal concessions or tax codes from one city (e.g., AMC) to queries concerning another city (e.g., PMC).
3. **Refusal Template:** Use the standard refusal template when asking about cross-jurisdictional combinations.
