# Skills: Single-Source Attribution

## Triggers
- Any request that queries multiple documents simultaneously.

## Core Constraint & Extraction Rules
- **CRITICAL RULE:** No cross-document blending allowed. 
- Every extracted fact or answer MUST end with a strict citation of the single source document it came from (e.g., "Source: policy_hr_leave.txt").