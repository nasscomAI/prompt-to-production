================================================================================
PULL REQUEST TITLE
================================================================================

[BENGALURU] Sivasubramanian — Vibe Coding Submission


================================================================================
PULL REQUEST DESCRIPTION
================================================================================

## Summary

This PR completes all four use cases of the NASSCOM prompt-to-production assignment with comprehensive implementations of AI-guided systems that handle real-world failure modes: taxonomy drift, scope bleed, obligation softening, cross-document blending, and hedged hallucination.

## UCs Completed

### ✅ UC-0A: Complaint Classifier
- **Objective:** Classify citizen complaints by category, priority, reason, and ambiguity flag
- **Core failure modes prevented:** Taxonomy drift, severity blindness, missing justification
- **Implementation:** Keyword-driven classifier with severity keyword enforcement
- **Output:** 15/15 test rows classified successfully (results_pune.csv)

### ✅ UC-0B: Policy Summarizer (Multi-Condition Enforcement Focus)
- **Objective:** Summarize policy documents while preserving ALL clauses and conditions
- **Core failure modes prevented:** Clause omission, scope bleed, obligation softening, condition dropping
- **Critical clause verification:** Clause 5.2 (LWP approval) explicitly preserves BOTH Department Head AND HR Director requirement
- **Output:** All 10 critical clauses extracted and preserved in summary_hr_leave.txt
- **Note:** Policy summarizer prevents the "condition drop" trap where multi-party approval requirements are silently reduced to single-party

### ✅ UC-0C: Budget Growth Calculator
- **Objective:** Compute per-ward per-category budget growth with formula display and null handling
- **Core failure modes prevented:** Wrong aggregation level, silent null handling, formula assumption
- **Implementation:** Per-period growth calculations with explicit formula display; refusal of aggregation requests
- **Null handling:** All 5 deliberate nulls detected, flagged with reasons, and excluded from calculations
- **Reference values verified:** Ward 1 Kasba Roads 2024-07 (+33.1%), 2024-10 (-34.8%) match expectations
- **Output:** growth_output.csv with 12 periods, 11 valid growth calculations, all formulas shown

### ✅ UC-X: Policy Q&A System (Single-Source Enforcement)
- **Objective:** Answer policy questions using single-source documents, refuse cross-document blended answers
- **Core failure modes prevented:** Cross-document blending, hedged hallucination, condition dropping
- **Critical trap test:** Personal phone question correctly answers from IT section 3.1 only (email + portal), does NOT blend with HR policy, does NOT invent non-existent permissions
- **All 7 test questions passed:**
  1. Carry forward leave → HR section 2.6
  2. Install Slack → IT section 2.3
  3. Home office allowance → Finance section 3.1
  4. Personal phone for work → IT section 3.1 (NO blending with HR)
  5. Flexible working culture → Exact refusal template
  6. DA + meal receipts → Finance section 2.6 (NO, prohibited)
  7. LWP approval → HR section 5.2 (BOTH approvers, not dropped)

## Enforcement Features

✅ **agents.md and skills.md present and updated** for all 4 UCs
✅ **No placeholder text** ([FILL IN] sections removed from all files)
✅ **Comprehensive enforcement rules** in all agents.md files
✅ **Skill definitions** with input/output/error_handling specifications
✅ **Output files generated and committed** for all UCs
✅ **Test results documented** for UC-X (test_results.txt)

## Commits Included

```
b77b5e1 - Add UC-X test results: all 7 questions passed, no cross-document blending
abcecfa - UC-X Complete: Implement policy Q&A system with single-source answers
cc85a3b - UC-0C Complete: Implement per-ward per-category budget growth calculator
9054945 - Add output files for UC-0A and UC-0B
5cecba9 - UC-0B Complete: Preserve all policy clauses with multi-condition enforcement
9e308f3 - UC-0A Complete: Implement complaint classifier with keyword-driven detection
```

## Testing & Verification

✅ UC-0A: Complaint classification tested on Pune dataset (15 rows)
✅ UC-0B: All 10 critical clauses verified in summary output
✅ UC-0C: Reference values and null handling verified
✅ UC-X: All 7 policy Q&A test questions verified with expected answers

## Files Changed

### UC-0A
- uc-0a/agents.md (filled in)
- uc-0a/skills.md (filled in)
- uc-0a/classifier.py (156 lines, fully implemented)
- uc-0a/results_pune.csv (output file)

### UC-0B
- uc-0b/agents.md (filled in)
- uc-0b/skills.md (filled in)
- uc-0b/app.py (115 lines, fully implemented)
- uc-0b/summary_hr_leave.txt (output file)

### UC-0C
- uc-0c/agents.md (filled in)
- uc-0c/skills.md (filled in)
- uc-0c/app.py (210 lines, fully implemented)
- uc-0c/growth_output.csv (output file)

### UC-X
- uc-x/agents.md (filled in)
- uc-x/skills.md (filled in)
- uc-x/app.py (193 lines, fully implemented)
- uc-x/test_results.txt (test output file)

## Key Learnings

1. **Condition Preservation:** Multi-condition obligations (e.g., requiring both Department Head AND HR Director approval) must be explicitly preserved in summaries. Dropping even one condition is a failure.

2. **Single-Source Enforcement:** Cross-document blending creates permissions that don't exist. UC-X demonstrates how to answer from one document only or refuse cleanly.

3. **Formula Transparency:** Showing calculations explicitly in output rows prevents silent assumptions. UC-0C demonstrates formula display for growth calculations.

4. **Null Handling:** Silent null skipping is a common failure. UC-0C explicitly flags every null with reason before proceeding with calculations.

5. **Refusal Templates:** Exact refusal text with no variations prevents hedged hallucination. UC-X uses a standardized template verbatim.

## Notes

- All code uses Python standard library only (no external dependencies)
- All implementations handle edge cases explicitly
- All test outputs verified against README reference values
- Ready for production deployment

================================================================================
