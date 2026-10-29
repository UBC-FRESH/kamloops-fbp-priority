# ADR 0005: Provisional 10-class HFI and WUI priority rule

Status: proposed; must be replaced in P1.5
Date: 2026-10-28
Issues: #1

## Context

The proposal says the FBP outputs will be classified into ten classes based on suppression efficacy
and combined with two WUI classes. It does not define the class breaks or the combination matrix.
The speed run needs a transparent placeholder so the pipeline can be exercised end to end.

## Decision

For the prototype only:

- HFI classes (kW/m): 0–500, 500–1,000, 1,000–2,000, 2,000–3,000, 3,000–4,000, 4,000–6,000,
  6,000–8,000, 8,000–10,000, 10,000–30,000, >30,000.
- WUI class 1 (Human Interface Buffer): priority = `ceil(HFI class / 2)` (1–5).
- WUI class 2 (Risk Class): priority = HFI class (1–10).
- Outside the WUI: priority 0.

Flame length is computed as `0.0775 * HFI^0.46` (Byram 1959).

## Consequences

- The prototype produces a legible priority map and a zonal summary.
- The rule is not a scientific result. It must be replaced by a cited, BCWS-approved rule before
  P4/P5 conclusions.
- The rule gives the high-density WUI the full HFI scale and the buffer half-scale. That is a
  policy choice, not an empirical finding.

## Alternatives considered

- Use only HFI, with WUI as a mask. Simpler, but it does not express the proposal's two WUI classes.
- Use a continuous HFI × WUI score and quantile classes. More flexible, but harder to explain and
  to compare across scenarios.
- Wait for the final rule before producing any map. Rejected for the speed run: the pipeline needs
  an end-to-end output to expose the data and compute constraints.
