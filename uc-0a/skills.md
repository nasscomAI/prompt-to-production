skills:
  - name: classify_sanitation
    description: Identifies complaints related to garbage collection, sewage, and public hygiene.
    input: Unstructured string containing the complaint text.
    output: Boolean indicating if the complaint is sanitation-related, and a confidence score (0.0 to 1.0).
    error_handling: Return false and 0.0 confidence if input is null or unreadable.

  - name: classify_water
    description: Identifies complaints related to water supply, leaks, drainage, and flooding.
    input: Unstructured string containing the complaint text.
    output: Boolean indicating if the complaint is water-related, and a confidence score (0.0 to 1.0).
    error_handling: Return false and 0.0 confidence if input is null or unreadable.

  - name: classify_roads
    description: Identifies complaints related to potholes, broken pavements, road construction, and street infrastructure.
    input: Unstructured string containing the complaint text.
    output: Boolean indicating if the complaint is roads-related, and a confidence score (0.0 to 1.0).
    error_handling: Return false and 0.0 confidence if input is null or unreadable.

  - name: classify_electricity
    description: Identifies complaints related to power outages, streetlights, sparking wires, and transformers.
    input: Unstructured string containing the complaint text.
    output: Boolean indicating if the complaint is electricity-related, and a confidence score (0.0 to 1.0).
    error_handling: Return false and 0.0 confidence if input is null or unreadable.

  - name: classify_other
    description: Acts as a fallback for complaints that do not clearly fit into predefined categories or cover multiple categories ambiguously.
    input: Unstructured string containing the complaint text.
    output: Boolean indicating if the complaint requires manual review or falls into 'Other', and a confidence score.
    error_handling: Return true for 'other' if the text cannot be processed by other classifiers.
