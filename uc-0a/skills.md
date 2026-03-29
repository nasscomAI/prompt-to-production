# Skills for Complaint Classifier

This document outlines the core capabilities (skills) the AI must demonstrate to resolve the Complaint Classifier use case.

### 1. Multi-Class Classification
* **Description:** The ability to accurately assign a complaint to one of four categories: Infrastructure, Billing, Safety, or General.
* **Target:** > 90% accuracy on test datasets.

### 2. Sentiment Analysis (Vibe Check)
* **Description:** Detecting the emotional state of the citizen (e.g., Angry, Calm, Urgent).
* **Target:** Flagging "Angry" or "Safety" issues for immediate human review.

### 3. JSON Structured Output
* **Description:** Ensuring the AI only responds in valid JSON format so the `classifier.py` script can read the data.