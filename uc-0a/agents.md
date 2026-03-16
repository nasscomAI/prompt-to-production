# Agent Definition: Complaint Classifier

This document defines the AI agents used for the Complaint Classifier (uc-0a), prioritized using the RICE framework.

## RICE Prioritization Table

| Agent | Role | Reach | Impact | Confidence | Effort | RICE Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Triage Bot** | Categorizes incoming complaints | 100% | High | 90% | 2 days | **High** |
| **Urgency Bot** | Flags high-priority/angry tones | 100% | Med | 80% | 1 day | **Med** |

---

## Agent Details

### 1. Triage Bot
* **Goal:** Read raw text and assign it to a department (Billing, Tech, Legal).
* **Justification:** This agent has the highest Reach because every single document must be categorized before anything