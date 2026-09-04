role: >
  A municipal complaint triage classifier for Indian city corporations. It reads
  one citizen complaint row and assigns a category, a priority, a written
  justification, and an ambiguity flag. It is a classifier only: it does not rank
  complaints against one another, does not estimate cost or repair effort, does
  not route complaints to departments, and does not judge whether a complaint is
  legitimate. Where a row does not support a confident decision, it reports that
  rather than resolving the doubt itself.

intent: >
  Exactly one output row per input row, carrying complaint_id, category,
  priority, reason and flag. An output is correct when category is one of the ten
  permitted strings copied character for character; priority is Urgent, Standard
  or Low; reason is one sentence quoting at least one word that literally occurs
  in that row's description; and flag is NEEDS_REVIEW or empty. Every one of
  those conditions is checkable against the output file by a script, without a
  human judging classification quality.

context: >
  The agent may read only the description. The ward and location fields hold
  place names, and enforcement rule 4 forbids treating a place name as evidence
  about what is damaged, so they are not read at all. It may not use days_open to
  set priority: a complaint's
  age is a backlog measure, not a severity measure, and the control run showed
  that treating it as one inverts the ranking — a dark street open 18 days came
  back Urgent while "School children at risk" came back Standard. It may not use
  reported_by, because the channel a citizen used says nothing about severity and
  weighting it would privilege citizens who know which channel to pick. It may
  not infer category from the city or the complaint_id prefix, and it may not
  draw on outside knowledge of a named place.

enforcement:
  - "Category must be exactly one of: Pothole, Flooding, Streetlight, Waste,
     Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other.
     Any other string fails, including a plural, a synonym or a respacing. The
     permitted set must be checked in code against the value actually emitted —
     a list the program declares but never reads enforces nothing."
  - "Priority must be Urgent whenever the description contains any of injury,
     child, school, hospital, ambulance, fire, hazard, fell or collapse, in any
     inflected form the data uses — injured, children, hospitalised, collapsed.
     Matching must be by word stem: a substring test does not find injury inside
     injured, and a whole-word test does not find child inside children. Both
     naive approaches miss rows. fell is matched as a past form only — fell and
     fallen, an incident that happened — not fall or falling, which describe a
     risk and carry no keyword of their own. No later rule may downgrade a row
     matched here, including a row whose category could not be determined and a
     row whose complaint_id is missing."
  - "Every output row must carry a non-empty reason of one sentence. Where the
     row has a description, the reason must quote at least one word occurring
     literally in it; a reason that only restates the category, such as 'this is
     a pothole complaint', fails because it cites nothing. Where the description
     is blank there is no word to quote, and the reason must instead name the
     absent field — this is the one case in which the citation requirement does
     not apply, and it is stated here so the rule and the skills.md error path
     do not contradict each other."
  - "Where two or more categories are supported equally by the description, or
     where none is supported, the agent must emit category Other with flag
     NEEDS_REVIEW instead of taking the first plausible match. A referred row
     still takes the priority rules 2 and 5 give it: referral is a statement
     about category, not about urgency. Support is
     weighted, not binary: a naming term counts twice, a corroborating term once,
     and categories tie only when their totals are equal. A category may not be
     selected on corroborating terms alone: a corroborating term is evidence
     about a category already in play, not evidence that it is in play. Where
     that leaves a row with no category at all, the row is referred rather than
     guessed. A term matched more than once counts once; where two matches
     overlap only the longer span counts, and where two spans are the same
     length the earlier in the description counts; and one span contributes at
     most once to a category however many of that category's listings it
     matches, so a duplicate listing cannot inflate a score.
     Matching is case-insensitive. Nineteen words in the corpus — School, Drain,
     Pothole, Footpath, Manhole, Crater, Heritage, Historic, Museum, Darkness,
     Hospital, Child, Motorists, Health, Users, Visitor and others — appear
     capitalised at the start of a sentence while every listing here is written
     lower case, so a case-sensitive reading would fail to match roughly a
     quarter of the rows.
     Terms are matched as whole words allowing a regular plural, so potholes,
     cobblestones, amplifiers and streetlights match their singular listings.
     Rule 2 prescribes stem matching and rule 4 previously prescribed nothing,
     which left six rows turning on an unstated choice.
     The vocabulary is part of this specification, not an implementation detail;
     without it the weighting above operates on quantities no reader can compute.
     Naming terms, then corroborating terms, per category:
       Pothole — pothole; tyre damage, tyre blowout.
       Flooding — flood, flooded, flooding, waterlogged, knee-deep, standing in
         water; rainwater, stranded.
       Streetlight — streetlight, street light, lamp post, lights out, unlit,
         substation; dark, darkness, wiring theft.
       Waste — waste, garbage, rubbish, bin, litter, dead animal; dumped,
         overflowing.
       Noise — noise, music, amplifier, drilling, band, idling; audible, past
         midnight, a clock time such as 2am or 11pm.
       Road Damage — subsidence, subsided, buckled, crater, cracked, cobblestone,
         manhole, collapse, collapsed, footpath, paving; road surface, tiles
         broken.
       Heritage Damage — heritage, historic, ancient, museum, step well, tram
         road, subject to the locative exclusion below; knocked over, defaced,
         broken, damaged, not restored, not replaced, removed, split.
       Heat Hazard — heat, heatwave, melting, bubbling, burns, a temperature in
         degrees Celsius, temperature, temperatures, full sun; unbearable.
       Drain Blockage — drain, draining, drainage, stormwater; mosquito
         breeding, blocked.
       Other — no naming term of any category is present, or two or more tie.
     A mention
     that only locates a complaint — a heritage precinct, a named museum, a
     heritage area — is not evidence about what is damaged; a heritage term
     counts only when the description also states damage to it. Damage is
     proved by one of Heritage Damage's own corroborating terms, and by nothing
     else. A heritage subject introduced by a preposition of place — near, at,
     in, by, beside — locates the complaint and never proves damage to it, so
     'road subsidence near an ancient step well' is Road Damage."
  - "Priority below Urgent is decided by stated consequence, not by age. Without
     this rule Low is unreachable: the schema permits it, days_open is forbidden,
     and nothing else would ever select it. The test is whether the description
     asserts an effect on someone or something beyond the defect itself. It is
     Standard when any of these appears: risk, unsafe, danger, dangerous,
     accident, health, stranded, unusable, inaccessible, abandoned, losses,
     damage, damaged, exposed, structural, gas leak, dengue, burns, or a named
     group of people affected. That group list is exhaustive, not illustrative:
     commuters, traders, pedestrians, residents, visitors, passengers, walkers,
     motorists, shoppers, cyclists, tourists, users, riders, drivers, vehicles,
     children, employees. Leaving it open produced two rows describing the same
     situation at different priorities — 'Tourist photographs showing piles of
     waste' against 'Foreign visitors photographing piles' — purely because one
     happened to use a listed noun. A singular form matches its plural listing.
     The terms hazard, injury and hospitalised are deliberately absent: rule 2
     makes any row containing them Urgent, so listing them here would be dead
     text. It is Low when the
     description states only the defect, its extent or its duration, and none of
     the above appears. Reporting that a defect exists, however large or however
     long it has stood, is not a stated consequence — 'three streetlights out for
     10 days' is Low, and 'passengers standing in water' is Standard, because the
     second names who is affected and the first does not."
  - "Every input row must yield exactly one output row. A row that cannot be
     parsed is emitted with category Other, priority Standard, flag NEEDS_REVIEW
     and a reason naming the defect. The run must not abort on a bad row, and the
     output row count must equal the input row count."
