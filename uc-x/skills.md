# skills.md — UC-X Ask My Documents

> Manually refined. These two skills are implemented as the functions
> `retrieve_documents` and `answer_question` in `app.py`. The descriptions below
> match that implementation exactly — input shape, output shape, and the
> error/edge behaviour are all testable against the code.

## Skill 1 — `retrieve_documents`

**Description.** Loads the three CMC policy files and parses each into a flat
list of sub-sections indexed by `(document_name, section_id)`, plus the
corpus-wide term/bigram frequencies used for IDF scoring. This is the
**only** place the agent touches the filesystem; everything downstream works on
the parsed index, so no answer can pull in text the indexer did not see.

**Input.**
- `data_dir` (optional `Path`, defaults to `Path(__file__).resolve().parent.parent / "data" / "policy-documents"`). Resolved from `__file__`, never from the cwd, so the skill works from the repo root and from inside `uc-x/`.

**Output.** A tuple `(sections, uni_freq, bi_freq)`:
- `sections` — `list[dict]`, one per sub-section. Each dict has:
  - `doc` — filename, e.g. `"policy_hr_leave.txt"`
  - `id` — sub-section number as a string, e.g. `"2.6"`, `"5.2"`
  - `heading` — the parent top-level title, e.g. `"ANNUAL LEAVE"`, `"PERSONAL DEVICES (BYOD)"`
  - `text` — the sub-section body, verbatim, with wrapping whitespace collapsed to single spaces
  - `heading_uni`, `body_uni` — `Counter` of canonical unigram terms in heading / body
  - `heading_bi`, `body_bi` — `Counter` of canonical bigram (adjacent-term) pairs in heading / body
- `uni_freq`, `bi_freq` — `dict[term, int]`; how many sections contain each unigram / bigram (used by IDF: `1 / (1 + freq)`).

**Parsing rules (testable).**
- Top-level headings match `^\d+\.\s+[A-Z ...]+$` (e.g. `2. ANNUAL LEAVE`) and become the `heading` of subsequent sub-sections.
- Sub-sections match `^\d+\.\d+\s+.+` (e.g. `2.6 Employees may ...`) and absorb continuation/indented lines until the next sub-section, heading, or separator.
- Box-drawing separator lines (`═══...`, no alphanumerics) and document header lines (`CITY MUNICIPAL CORPORATION`, `Version:`, `Document Reference:`) are ignored.
- Tokenisation lowercases, drops tokens shorter than 3 chars, drops a fixed stopword list, folds a narrow synonym set (`phone`/`devices`→`device`; `installing`→`install`; `approves`→`approval`; `claimed`→`claim`; etc.), and collapses any object of `install` to `software` (so "install Slack" matches "install software"). It deliberately does **not** fold `working`→`work` or `laptop`/`computer`/`smartphone`→`device` (those bridges cause cross-document bleeding).

**Error handling.**
- If any of the three files is missing, raise `FileNotFoundError` naming the missing path. The agent never falls back to an empty index or a guess.
- An unreadable/malformed file surfaces as the raw `UnicodeDecodeError`; there is no silent skip.

---

## Skill 2 — `answer_question`

**Description.** Given one question, returns either a single-source answer
with citation or the verbatim refusal template. This skill is the **only**
producer of user-facing text, and it enforces the single-source,
no-hedging, always-cite rules from `agents.md`.

**Input.**
- `question` (`str`) — the user's natural-language question.
- `sections`, `uni_freq`, `bi_freq` — the index returned by `retrieve_documents`.
- `debug` (`bool`, default `False`) — when true, prints the question's terms, bigrams, and the top-8 section scores to stderr/stdout for diagnosis.

**Output.** A single `str`, exactly one of:
1. `<section text> Source: <doc> §<id>` — the verbatim text of the single best section followed by its citation.
2. The refusal template (see `agents.md` R3), byte-for-byte.

**Algorithm (deterministic, testable).**
1. Tokenise the question into unigrams and bigrams (same tokeniser as the indexer). If no signal terms remain, return the refusal template.
2. Score every section with IDF-weighted overlap using **binary** term frequency (a section either addresses a term or it does not — repeating a word inside an example list must not inflate the score), with heading terms weighted `HEADING_WEIGHT` (= 2.0) and bigrams weighted `BIGRAM_WEIGHT` (= 2.5) over unigrams. A term found in the heading is counted **only** at heading weight (no double-count with the body).
3. Sort by score descending; ties broken by smaller section number (R6).
4. If the best score `< MIN_CONFIDENCE` (= 0.60) → refusal (no document confidently answers).
5. **Cross-document guard (R1):** if any section from a *different* document than the best scores `>= best - CROSS_DOC_MARGIN` (= 0.10) → refusal (the question spans documents; refuse rather than blend).
6. Otherwise return the best section's verbatim text + `Source: <doc> §<id>`.

**Why this design (the three named failure modes).**
- *Cross-document blending* is blocked by step 5 plus the bigram scoring: the personal-phone question's phrase `personal device` is a bigram owned by IT §3.1's heading, while `work ... from home` in that question is **not** the contiguous `work from home` bigram in Finance §3, so Finance can never win on a phrase match and IT §3.1 is returned alone.
- *Hedged hallucination* is blocked because there is no third output shape — a low-confidence or cross-document question can only hit the refusal template; there is no code path that emits "while not explicitly covered...".
- *Condition dropping* is blocked because the returned text is the section's full body, never a summary — both LWP approvers, the DA+meal prohibition, and the 31 December forfeiture date all survive.

**Error handling / edge cases.**
- Empty or whitespace-only question → refusal template (no signal terms).
- Question with no overlap to any section (e.g. "flexible working culture") → refusal template (best score < `MIN_CONFIDENCE`).
- Question that triggers the cross-document guard → refusal template (never a blended answer).
- The refusal string is a module constant (`REFUSAL`); it is never constructed dynamically, so it can never drift from the required wording.
