# CLAGN Variability Search

A systematic, all-sky, **both-direction** (turn-on *and* turn-off) search for
changing-look AGN (CLAGN), selected from joint **mid-IR (NEOWISE) + optical (ZTF)
+ X-ray (eROSITA)** variability — with a **characterized selection function** as
the headline deliverable.

Built on the **NASA Fornax Science Console**, reusing the
[`nasa-fornax/fornax-demo-notebooks`](https://github.com/nasa-fornax/fornax-demo-notebooks)
`light_curve_collector` / `scale_up` pipeline for light-curve assembly.

See **[PLAN.md](PLAN.md)** for the full science case, novelty positioning,
pipeline, selection criteria, and milestones.

## Layout

```
notebooks/   analysis notebooks (run on Fornax)
  01_smoke_test.ipynb     validate the pipeline on 5 known CLAGN  <-- START HERE
src/         project-specific Python
  smoke_test_targets.py   the 5 validation CLAGN
  selection.py            variability metrics + literature-calibrated thresholds
data/        local data products (gitignored)
```

## Status

Planning + scaffold complete. Next action: run `01_smoke_test.ipynb` on the
Console and confirm the known mid-IR / optical events are recovered.
