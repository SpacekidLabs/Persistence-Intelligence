# Roadmap

This is a living document, not a spec. Update it after every experiment that
changes what we believe. If a section here gets contradicted by real data,
rewrite the section — don't leave it standing next to the data that disproved it.

The core discipline this project is trying to hold itself to:

> Illustrative numbers, mock runs, and hoped-for outcomes do not become the
> narrative. Only measured numbers do. Anything in this document that isn't
> backed by a run you can point to is a hypothesis, and should read like one.

---

## Where we are

- [x] Experiments 01-04 (signal persistence, competing resonances, modal
      objects, feedback systems) - each generates a signal, tracks one or
      more structures through time, and produces a dashboard plot.
- [x] Metric harmonization - all four experiments now compute
      `survival_time`, `stability`, and `recurrence_mean` via the same
      shared functions (`persistence.trackers`, `persistence.recurrence`),
      so structures from different experiments are comparable instead of
      living in four separate vocabularies.
- [x] Taxonomy tooling (`05_persistence_taxonomy.py`) - loads exported
      metrics, builds a High/Medium/Low comparison table, computes pairwise
      disagreement rates between metrics, and runs PCA/correlation/k-means
      as a secondary view.
- [ ] **Run 05 on real measurements.** Not done yet. Every number discussed
      in this project so far has been illustrative - constructed to test
      the tooling, not measured from an actual run. This is the next step,
      and nothing below is final until it happens.

---

## The open question

Is persistence one thing or several?

```
Possibility A          Possibility B           Possibility C
                                                  
Weak <----> Strong     Resonances | Modal |      Mostly one continuum,
                        | Feedback                but recurrence-rich
one axis, all four      (separate, unrelated      structures consistently
experiments measure     clusters by origin)       peel away from it
the same thing                                    
                                                  -> Energy Persistence
                                                     Identity Persistence
                                                     Recurrence Persistence
                                                     (or similar - exact
                                                     names TBD by what the
                                                     data actually shows)
```

`05`'s job is to produce evidence for which of these three is closest to
true, via two independent views of the same 19-structure table:

1. **Direct**: pairwise disagreement rate between `survival_time`,
   `stability`, `recurrence_mean` on a High/Medium/Low bucketing.
   - All three pairs disagree at similarly low rates -> **A**.
   - Structures split into origin-based clusters with no shared pattern
     across experiments -> **B**.
   - `survival_time`/`stability` agree with each other far more than
     either agrees with `recurrence_mean`, and the disagreement is
     concentrated in recurrence-rich structures (feedback harmonics,
     anything periodic) -> **C**.
2. **Indirect**: PCA scatter colored by source experiment, as a sanity
   check on the same conclusion from a different angle.

The mock run produced a C-shaped result (26% disagreement between
survival/stability, 63-74% between either and recurrence).

This is not evidence about the real signals.

It demonstrates that the analysis pipeline is capable of producing
distinct outcomes for A-like and C-like synthetic test cases. Whether the
pipeline behaves usefully on real measurements remains to be determined.

---

## What would make the project fail?

This section exists to give the project permission to be wrong. A,
B, and C above are all framed as ways "persistence" survives as a useful
idea in some form. That's an incomplete list - it's also possible the
whole premise doesn't hold up, and the roadmap should say what that looks
like instead of only planning for success.

The project should be reconsidered - narrowed, redirected, or abandoned -
if any of the following happen:

- **No stable metric structure emerges across experiments.** If every new
  experiment needs its own bespoke metrics with no overlap with what came
  before (the way 01-04 originally did, before harmonization), that's a
  sign there's no shared underlying object - just four separate
  measurements that happen to share a name.
- **Experiment origin explains the variance better than any persistence
  metric does.** If structures cluster by *which experiment produced
  them* rather than by survival/stability/recurrence values - i.e. if
  Outcome B holds, cleanly - then "persistence" isn't doing explanatory
  work. The experiments would be measuring four different things that a
  shared vocabulary happened to paper over.
- **New experiments keep requiring entirely new metrics.** If 06, 07, and
  beyond each need a metric that doesn't fit `survival_time`,
  `stability`, or `recurrence_mean` - and that pattern keeps repeating
  with no sign of converging on a small fixed set - the project may be
  generating an open-ended list of unrelated measurements rather than
  discovering a finite set of axes.
- **No common vocabulary survives contact with new domains.** If a
  cross-domain check (see "candidate later experiments" below) shows the
  axes found in audio don't transfer to even simple non-audio signals,
  that weakens the claim that this is about persistence-in-general rather
  than persistence-in-audio-signals-with-these-four-specific-constructions.

If one or more of these hold, the honest move is not to keep adding
experiments hoping the next one clarifies things. It's to say plainly that
"persistence" may not be a useful primitive at the scope this project
started with, and either narrow the scope (e.g. "persistence in
resonant/modal audio signals," dropping the universal framing) or stop.

That outcome would still be a real result. A negative result - "this
unification doesn't hold" - is not a failure of the research, only of the
roadmap's optimistic branches.

---

## Immediate next steps

- [ ] Run `01` through `04`, confirm `experiments/results/*.json` populates
      with real, non-null `survival_time` / `stability` / `recurrence_mean`
      for all 19 structures.
- [ ] Run `05`, capture the comparison table, disagreement rates, and PCA
      plot.
- [ ] Read the disagreement rates against A/B/C. Be honest about
      ambiguous cases - if all three pairwise rates land within ~15
      percentage points of each other, that's a genuine middle case
      between A and C, not evidence for either.
- [ ] Update this document's "Where we are" and "The open question"
      sections with what was actually found, replacing the mock-run
      caveat with a real result.

## Experiment 06 - contingent design

06 should not be designed until the above is done, because its design
depends on the answer:

- **If A** (one axis): 06 becomes a *resolution* test, not a boundary test.
  Take one structure and sweep a single parameter (e.g. decay time) finely
  enough to see whether `survival_time`/`stability`/`recurrence_mean` move
  together smoothly across the whole range, or whether there's a regime
  change hiding inside what looked like one axis from four coarse samples.
- **If B** (unrelated categories): 06 becomes a *vocabulary* question, not
  a signal-processing one - is "persistence" even the right word to keep
  using across resonance, modal, and feedback structures, or should the
  project fork into three differently-named investigations?
- **If C** (continuum + peel-away), which is the live hypothesis right now:
  06 becomes **"Where does recurrence diverge?"** - a stress test that
  starts at a structure with low recurrence (pure decaying sine) and
  gradually introduces recurrence-producing structure (interruptions,
  repetition, then an explicit feedback loop), tracking all three metrics
  continuously across the transformation:

  ```
  Pure sine
    -> sine with decay
    -> sine with frequency drift
    -> sine with interruptions
    -> repeating impulse train
    -> feedback loop
  ```

  The thing to look for: a point along this chain where `recurrence_mean`
  stops moving with `survival_time`/`stability` and starts moving
  independently. That point - not "feedback systems in general" - is the
  actual fault line, and it's only findable by sweeping continuously
  instead of comparing four isolated experiments.

Whichever branch applies, 06 gets designed and written only after the real
05 run, as its own step - not pre-built now.

---

## If a fault line is found: sketch of a framework phase

This section is deliberately speculative and should be treated as such.
Nothing here is committed work - it's what *might* come next if 06
confirms a genuine multi-axis structure, so that direction isn't invented
from scratch under time pressure later.

### What "framework" would mean here

Not a grand unified theory of persistence. A minimal shared interface that
every future experiment reports into, replacing today's per-experiment
metric dicts with something structured enough to compare automatically
instead of requiring a coverage-filtered taxonomy script each time.

A plausible shape, **not to be committed to until 06 confirms which axes
are real**:

```python
@dataclass
class PersistentStructure:
    name: str
    source_experiment: str

    # One sub-score per confirmed axis - the field names below are
    # placeholders for whatever 06 actually finds, not predictions.
    energy_persistence: float | None      # survival_time / stability lineage
    recurrence_persistence: float | None  # self-similarity lineage
    identity_persistence: float | None    # speculative third axis - only
                                           # add this if a third pattern
                                           # shows up, don't pre-build it
```

The discipline to hold here: **add a field only after an experiment
produces a metric that doesn't fit the existing fields.** Adding
`identity_persistence` before any experiment has measured something that
`energy_persistence` and `recurrence_persistence` can't already explain
would be designing the framework around the hope of a third axis instead
of evidence for one.

### Candidate later experiments (unordered, unscheduled, not committed)

These are things that would become worth doing _if_ a multi-axis result
holds up, listed so they don't get lost - not a queue.

- **07 - Cross-domain check**: does the same axis structure show up in a
  non-audio signal (e.g. a simple time series, a random walk with
  occasional resets)? If the axes are about signals-in-general and not
  audio-specific quirks, this should still show a similar split.
- **08 - Adversarial structures**: deliberately construct a signal meant
  to score high on one axis and low on another (e.g. high recurrence, low
  energy survival, by design) and confirm the metrics actually track it -
  a check on whether the axes are real or an artifact of the specific
  signals used in 01-04.
- **Possible refactor**: once axes are confirmed, consider whether
  `persistence/trackers.py` and `persistence/recurrence.py` should be
  reorganized around the axes themselves rather than around "energy
  trace" vs "recurrence trace" as implementation categories.

### What would make this section wrong

If 06 shows recurrence rejoining the main continuum at some parameter
value rather than diverging further, that's evidence for Possibility A
after all (one axis, with 04's feedback structures just sitting at an
extreme point on it) - and this whole section should be deleted, not kept
around as a "maybe later."

---

## Working principle for this document

Every checkbox above should correspond to something that actually ran and
produced output you looked at - not something that seems like it should be
true based on the shape of the story so far. When in doubt, the move is
always: run it, then write down what happened.

The same discipline applies to the failure conditions above: if one of
them starts to look true, the right response is to update this document
to say so, not to find a reason the data doesn't really count.
