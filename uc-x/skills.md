# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_traffic_evidence
    description: Collect or accept traffic, route, incident, and civic evidence with freshness information.
    input: Origin, destination, permitted source or supplied evidence.
    output: Verified route candidates and evidence status.
    error_handling: Mark live traffic unavailable when it cannot be verified.

  - name: recommend_route
    description: Compare supplied routes and recommend the least affected supported option.
    input: Origin, destination, route candidates, and evidence.
    output: Recommended route, condition, reason, and traffic-data status.
    error_handling: Ask for missing origin or destination; do not guess routes.
