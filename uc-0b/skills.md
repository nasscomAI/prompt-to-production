skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input:
      type: string
      format: file path (e.g., "../data/policy-documents/policy_hr_leave.txt")
    output:
      type: object
      format: |
        {
          "sections": [
            {
              "number": "2.3",
              "content": "14-day advance notice required"
            }
          ]
        }
    error_handling: |
      - Invalid path: return error {"error": "File not found"}
      - Malformed document: return raw text with warning {"raw_content": "...", "warning": "Could not parse sections"}
  
  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving all 10 clauses with references.
    input:
      type: object
      format: |
        {
          "sections": [
            {
              "number": "2.3", 
              "content": "..."
            }
          ]
        }
    output:
      type: string
      format: Plain text summary with clause references (e.g., "2.3: 14-day advance notice required (must)")
    error_handling: |
      - Missing clauses from inventory: flag omissions and quote verbatim
      - Condition dropping detected: preserve ALL conditions or error with specifics
      - Scope bleed detected: reject output containing "standard practice", "typically", etc.