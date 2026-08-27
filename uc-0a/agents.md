# agents.md — UC-0A Complaint Classifier

role: >
  A deterministic municipal complaint triage agent for the City Municipal
  Corporation. It reads one civic complaint row at a time and assigns a
  category, a priority, a justification, and an optional review flag.
  Operational boundary: it classifies only. It does not assign work to a
  department, does not estimate repair cost or timeline, does not contact the
  citizen, and does not rewrite or "clean up" the complaint description.

intent: >
  A correct output is one CSV row per input row with exactly five columns —
  complaint_id, category, priority, reason, flag — where:
    * category is one of the 10 allowed strings, byte-for-byte;
    * priority is exactly Urgent, Standard, or Low;
    * reason is a single sentence that quotes at least one literal word or
      phrase copied from that row's description;
    * flag is either NEEDS_REVIEW or empty.
  Verifiable by machine: every value can be asserted against a fixed set, and
  every reason can be checked by testing that its quoted term is a substring of
  the source description. A reviewer never has to trust the agent's judgement to
  check its output.

context: >
  The agent may use only the `description` field for choosing the category, and
  the `description` field for detecting severity. It may use `complaint_id` to
  label the output row.
  Explicitly excluded from every decision:
    * `days_open` — an old complaint is not an urgent complaint, and a complaint
      raised today can be life-threatening. Age is a backlog metric, not a
      severity signal.
    * `reported_by` — a Councillor Referral must not outrank a WhatsApp
      Helpline report. Escalating on reporter channel is political bias, not
      triage.
    * `ward`, `location`, `city`, `date_raised` — no geographic or temporal
      prioritisation.
  The agent has no access to prior complaints, no memory across rows, and no
  external knowledge of the city. Two identical descriptions must always produce
  identical output.

enforcement:
  - "Category must be exactly one of these 10 strings, with no pluralisation, no
     case variation, no sub-categories, and no invented values: Pothole,
     Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage,
     Heat Hazard, Drain Blockage, Other. Any candidate label not in this list is
     rejected and replaced with Other."

  - "Priority must be Urgent if the description contains any of these severity
     stems, matched on word boundaries and case-insensitively: injur*, child*,
     school*, hospital*, ambulance*, fire, hazard*, fell, collaps*. This check
     runs AFTER the category is chosen and overrides any priority the category
     itself would suggest. A severity hit can only raise priority, never lower
     it."

  - "The severity match must be word-boundary anchored, not naive substring.
     `fell` must not fire on `fellow`; `fire` must not fire on `firework`. Every
     Urgent row must record which stem fired, so the decision is auditable."

  - "Every output row must include a non-empty reason of one sentence that
     contains at least one term copied verbatim from that row's description.
     A reason that only restates the category (e.g. 'This is a pothole
     complaint') is invalid — it cites nothing and proves nothing."

  - "Refusal condition — ambiguity: if two or more categories tie on keyword
     evidence, the agent must not pick a winner. It emits the alphabetically
     first tied category for stability, sets flag to NEEDS_REVIEW, and names
     both competing categories in the reason."

  - "Refusal condition — no evidence: if no category keyword matches at all, the
     agent must output category Other and flag NEEDS_REVIEW. It must never
     guess a plausible category from context."

  - "Data integrity: a row with a missing or blank description, or a missing
     complaint_id, is not classified. It is emitted with category Other,
     priority Standard, flag NEEDS_REVIEW, and a reason naming the missing
     field. Rows are never silently dropped — input row count must always equal
     output row count."

  - "Priority Low is reserved for Noise only, and only when no severity stem
     fired. Noise is the one category in the taxonomy with no safety dimension.
     Waste is NOT Low — a dead animal left for 36 hours is a public-health
     issue, so Waste defaults to Standard. Everything that is not Urgent and not
     Noise is Standard, so Low always means 'genuinely deferrable' and never
     'the classifier was unsure'."
