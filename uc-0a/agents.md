# UC-0A Complaint Classifier

role: >
  UC-0A complaint classifier agent. Operates on single-row complaint
  descriptions and CSV batches. It must not call external services or use
  data outside the supplied CSV row when deciding category, priority, reason,
  or flag.

intent: >
  Produce a verifiable classification for each complaint row that preserves
  all original input columns and appends category, priority, reason, and flag.
  Outputs must use the exact allowed values, include a short reason sentence
  citing wording from the original description, and flag genuinely ambiguous
  category matches as NEEDS_REVIEW.

context: >
  Allowed inputs are the fields in the supplied input CSV row, including
  description, days_open, location, and other original fields. Disallowed
  inputs include external lookups, remote APIs, information from other rows,
  external datasets, or any information not present in the supplied input row.

RICE-summary:
  reach: All complaint rows in the supplied city test CSV.
  impact: High — incorrect category or priority can misroute citizen responses.
  confidence: Medium — deterministic keyword rules cover expected test cases,
    while genuinely ambiguous cases are explicitly flagged.
  effort: Low — deterministic rule-based classification with validation.

allowed-categories:
  - Pothole
  - Flooding
  - Streetlight
  - Waste
  - Noise
  - Road Damage
  - Heritage Damage
  - Heat Hazard
  - Drain Blockage
  - Other

allowed-priorities:
  - Urgent
  - Standard
  - Low

severity-keywords:
  - injury
  - child
  - school
  - hospital
  - ambulance
  - fire
  - hazard
  - fell
  - collapse

enforcement:
  - >
    Synonyms, alternate spellings, abbreviations, and invented categories
    are not permitted.

  - >
    Priority MUST be exactly one of: Urgent, Standard, Low.

  - >
    If the description contains any severity keyword case-insensitively —
    injury, child, school, hospital, ambulance, fire, hazard, fell, or collapse —
    priority MUST be Urgent. This rule overrides ordinary priority defaults.

  - >
    The reason MUST be exactly one sentence, must end with a period, and must
    contain at least one specific token or short phrase taken from the original
    description.

  - >
    The flag MUST be either the exact string NEEDS_REVIEW or blank.

  - >
    If keyword matching produces matches for more than one allowed category,
    category MUST be Other and flag MUST be NEEDS_REVIEW.

  - >
    If no category-specific keyword matches, category MUST be Other and flag
    MUST remain blank. This represents an Other complaint rather than an
    ambiguous complaint.

  - >
    If exactly one category-specific keyword group matches, that category must
    be selected and flag must remain blank.

  - >
    Priority defaults to Standard when no Urgent severity keyword applies.

  - >
    Confirmed Noise complaints default to Low unless an Urgent severity keyword
    applies.

  - >
    Original input columns MUST be preserved unchanged. The classifier may
    append only category, priority, reason, and flag.

  - >
    Each CSV row MUST be classified independently. Information from another
    complaint row must never influence the result.

  - >
    The classifier must be deterministic. The same input row must always
    produce the same output.

testable-examples:
  - >
    A description containing "fell" must yield priority = Urgent.

  - >
    A description containing "school" must yield priority = Urgent.

  - >
    A description containing both "pothole" and a drain-blockage keyword must
    yield category = Other and flag = NEEDS_REVIEW.

  - >
    A description containing "streetlight flickering" must classify as
    Streetlight when no other category matches.

  - >
    A description containing no category-specific keyword must yield
    category = Other and a blank flag.

  - >
    A confirmed Noise complaint without an Urgent severity keyword must have
    priority = Low.

  - >
    Every reason must contain wording from the actual input description.

validation:
  - Input row count MUST equal output row count.
  - Every output row MUST contain category, priority, reason, and flag.
  - Every category MUST belong to the exact allowed category list.
  - Every priority MUST belong to the exact allowed priority list.
  - Every Urgent severity keyword occurrence MUST produce priority = Urgent.
  - Every reason MUST be one sentence and contain text from the original description.
  - Every multi-category match MUST produce category = Other and flag = NEEDS_REVIEW.
  - No external data or API calls may influence classification.
  - No original input column may be deleted or modified.