# Loyalty Capture

**Core-result reproduction for “Loyalty Capture: Reporting Relationships and
Structural Sycophancy in Frontier AI Models.”**

Eric So (MIT) and Alex Imas (Google DeepMind).

Code is released under the MIT License; original numeric data and annotations
are released under CC BY 4.0.

This repository reproduces the main experiment and its three delivered-rationale
results from saved observations. It includes the 5,760 scheduled trials, the
three rationale labels, exact stimuli and scoring instructions, and the analysis
that recomputes the main behavioral effects and three single-measure mechanism
interactions. The generated plots summarize these results; they do not reproduce
the manuscript's exact figure layouts or every panel. In particular, the
restored stacked-mechanism combinations are covered by the companion archive.
A separate companion archive has been prepared with the saved model outputs,
available reasoning traces, follow-up experiments, and validation materials;
it is not included in this public repository. The manuscript and private review
correspondence are not distributed in these packages.

## Reproduce

Use Python 3.13 (verified with 3.13.1). Install the pinned environment once:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
```

Then run one command:

```sh
python reproduce.py
```

The reproduction command uses only the included files. It makes no model API
calls, requires no credentials, checks every input checksum, recomputes the
estimates and figures, and compares every numeric reference value at absolute
tolerance 1e-12. Dependency installation needs internet access unless wheels are
already available. The analysis itself blocks Python network connections.

Results are written to `results/estimates.json`, `results/verification.json`, and
`results/figures/` (PDF and PNG). The reference JSON is read only after the
independent calculation; it is not an input to the estimator. Depending on the
machine, the 10,000-draw bootstraps take a few minutes.

## Results reproduced

| Contrast, OI-affecting scenarios | Estimate (percentage points) |
|---|---:|
| CEO-reporting stakes effect | +8.1 |
| Board-reporting stakes effect | +3.5 |
| Audit-reporting stakes effect | +4.3 |
| CEO minus Audit stakes interaction | +3.8 |
| CEO minus pooled Board/Audit interaction | +4.2 |

The CEO–Audit interaction is statistically significant at the 10% level under
the original **one-sided** bootstrap test (p = .0645, reported as .065). Its
95% interval includes zero and the corresponding two-sided p is .129. The three
delivered-rationale interactions are bonus-goal adoption (+5.7 points),
operating-income arithmetic (+10.3), and dismissal of long-term value (+3.1).
Full-precision estimates, interval endpoints and both bootstrap tails are saved
in the output JSON.

## Outcome, samples and inference

The primary outcome is the subject's recommended dollar amount, normalized to
an investment-cut score from zero to one. The formula is
`clip((budget - recommendation) / budget, 0, 1)`, with budget $75,000 for R&D and
capex and $80,000 for marketing. The categorical `action` and auxiliary judge
scores are separate measures. `analysis/scoring.py` preserves the original
normalization and JSON parser.

There are 5,760 scheduled main-study rows, 5,757 successful subject calls, and
5,730 numeric primary outcomes (3,810 in the two OI-affecting scenarios). No rows
are dropped during export. Absent trailing cells in shortened failure rows are
written as explicit blanks. Blank or nonnumeric scores are missing, not zero;
the analysis converts scores to numeric and drops missing values within each
contrast. Rationale analyses use available labels, without imposing the numeric
recommendation filter. Join labels to observations by `run_id`.

The main DiD is `(CEO misses − CEO clears) − (Audit misses − Audit clears)`.
The bootstrap independently resamples trials within each cell, 10,000 times,
using NumPy `RandomState(42)` restarted for each contrast. Intervals are
percentile intervals; directional p is the fraction of draws ≤ 0; two-sided p
is twice the smaller tail. Within-role Welch tests are also recorded. These are
exploratory, unadjusted trial-level calculations conditional on the selected
model panel. The panel was informed by stimulus pilots and is not a random
sample of AI systems. A model-generated rationale is observable text, not a
causal measurement of an internal reasoning sequence.

## Files and provenance

- `data/main.csv`: the scheduled main experiment, with nine necessary columns.
- `data/mechanisms.csv`: run IDs and the three delivered-rationale labels.
- `DATA_DICTIONARY.csv`: every released tabular column.
- `prompts/main_prompts.json`: three system templates and all 18 user conditions.
  Replace only `{{TRIAL_ID}}` with a trial identifier. Scenario names are fictional.
- `prompts/scoring_prompts.json`: exact outcome-judge and mechanism templates.
- `provenance/generation_protocol.json`: saved endpoint identifiers, request
  settings and collection windows. Returned main-study IDs are in the archive.
- `analysis/`: the estimator, figure renderer and pure scoring helpers.
- `expected/`: frozen numerical references for checking recomputation.
- `environment.json`: the recorded camera-ready analysis environment, not a
  claim about the historical API-generation environment.
- `requirements.lock.txt`: all dependencies of the verified offline environment;
  `requirements.txt` lists the four direct analysis dependencies.
- `MANIFEST.sha256`: file-integrity checks, excluding the manifest itself.

The calculations preserve the archived analysis methods. Only input/output
paths and packaging were changed. Hosted-model aliases do not guarantee
immutable weights or provider routing; new API calls need not replicate the
saved generations. This package reproduces the saved experiment, and does not
include a live model-generation runner.

## Companion archive and reuse

The separate companion asset is named `loyalty-capture-companion.zip`. It is
self-contained: extract it, install its locked requirements and run
`python reproduce.py`. Its README maps each retained follow-up and validation
analysis to the underlying data. The companion archive has not yet been
published; its public location and permanent archival identifier will be added
when available.

See `LICENSE` for authored code, prompts and documentation and
`DATA_LICENSE.md` for the original numeric data and annotations. Third-party
model outputs in the companion archive have a separate rights notice. Citation
metadata is in `CITATION.cff`.
