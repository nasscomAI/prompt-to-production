# skills.md — UC-0C Budget Growth Calculator 

skills:
  - name: load_dataset
    role: >
      A data ingestion worker designed for strict retrieval and structural evaluation without applying financial logic.
    intent: >
      To scan the raw `.csv` input, validate columns against schemas, and perform a strict diagnostic accounting of any missing `actual_spend` values.
    context: >
      Responsible only for the ingestion pipeline and identifying blank inputs. Possesses no context regarding growth calculations or aggregate bounds.
    enforcement:
      - "Must read the source CSV exactly matching the specified file path."
      - "Must identify, count, and report the specific row details of any missing data in the `actual_spend` column."
      - "Must return clean downstream access to the data structure without modifying values."

  - name: compute_growth
    role: >
      A stringent mathematical engine restricted to calculating deterministic growth variables over isolated granular parameters.
    intent: >
      To accept exact filtration constraints (`ward`, `category`, `growth_type`), execute the specified equation on the data correctly, and return a tracking table showcasing the methodology.
    context: >
      Operates effectively blind beyond the explicitly requested filtration inputs. Incapable of assumptions, defaulting metrics, or executing global queries.
    enforcement:
      - "Must ensure computation strictly restricts calculations explicitly within the requested ward and category boundaries."
      - "Must output a visible, exact representation of the mathematical formula used in every row alongside the computed growth percentage."
      - "Must intercept null `actual_spend` triggers and clearly return the explicit warning from `notes` rather than executing computation across empty references. "
