# Plan: Variability-Selected CLAGN Search on Fornax

*Last updated: 2026-06-29*

## 1. Science goal & novelty

**Goal.** Build a uniform, all-sky catalog of changing-look / extreme-variability
AGN selected *jointly* from mid-IR (NEOWISE), optical (ZTF), and — where public —
X-ray (eROSITA) variability, with a **quantified selection function**.

**Novelty framing (important).** The tri-band concept is *not* itself novel —
López-Navas et al. 2023 already used IR+optical+X-ray, and Yang et al. 2024
selected 70 turn-on CLQs from joint ΔW1&ΔW2 + ZTF-g. Do **not** pitch "first to
combine bands." Pitch instead:

> The first **systematic, all-sky, both-direction (turn-on AND turn-off),
> characterized-selection-function** variability-selected CLAGN sample of the
> post-NEOWISE / eROSITA-DR1 era, spanning the southern sky and feeding
> LSST / SDSS-V / 4MOST follow-up.

The four gaps that survive 2026 review:
1. **Both directions + all-sky/southern-inclusive.** Competitors are turn-on-only
   and northern / eROSITA-DE-half; the southern sky has no unified CLAGN compilation.
2. **A characterized selection function** — completeness, purity, bias, occurrence
   rate. The Ricci & Trakhtenbrot 2023 review explicitly asks for this. **This is
   the headline contribution.**
3. **Cross-band variability as a physical-mechanism discriminator** (obscuration
   vs. disk-instability vs. TDE) via per-object relative amplitudes/lags.
4. **Timing hook:** closed full NEOWISE mission (2024), eROSITA DR1 variability
   catalog (Boller 2025), and Einstein Probe are all 2024–2026 arrivals.

## 2. Parent sample

- Base catalogs: Milliquas, WISE AGN color-selected (Assef R90/C75),
  SDSS/DESI spectroscopic AGN **+ normal galaxies** (turn-on events appear in
  objects previously classified inactive — that's the discovery space).
- Union → de-duplicate → ~10^5–10^6 objects.
- Define a clean **footprint mask** (ZTF + NEOWISE coverage; eROSITA-DE where used)
  up front — the selection function depends on it.

## 3. Data & archives (all confirmed available, 2026)

| Band | Source | Status |
|------|--------|--------|
| Mid-IR | NEOWISE **2024 final release** (full 2010/2014–2024, ~11 yr) | Public at IRSA + AWS Open Data |
| Optical | ZTF **DR23** + IRSA Forced Photometry Service | Public; DR24 pending |
| X-ray | eROSITA **DR1** (eROSITA-DE western hemisphere, ~half-sky, 1 epoch) | Mirrored at HEASARC → reachable from Fornax. **DR2 ~mid-2026** adds epochs (v2 upgrade). |
| Confirmation | DESI DR1 (Mar 2025) + SDSS-V Black Hole Mapper repeat spectra (± LAMOST) | Public / incremental |

**X-ray caveat:** DR1 is essentially single-epoch → use as *corroboration*, not a
variability trigger. Einstein Probe + eROSITA DR2 are the variability upgrades.

## 4. Pipeline on Fornax

Reuse `nasa-fornax/fornax-demo-notebooks`:
- **`light_curve_collector`** — multi-archive light curves for a source list
  (ZTF, WISE/NEOWISE, Gaia, Pan-STARRS, HEASARC X-ray, …).
- **`scale_up`** — same, for large samples.

Architecture:
1. **Sample assembly** (single node): build + mask parent catalog → partition by HEALPix.
2. **Light-curve construction** (batched fan-out via `scale_up`): one task per chunk.
   Output uniform per-object multi-band light curves (Parquet).
3. **Variability feature extraction** (batched): metrics per object/band (§5).
4. **Candidate selection** (single node): apply cuts → rank.
5. **Vetting + tiering** (semi-auto + by-eye on top candidates).

**Compute constraint (real):** Fornax Dask is **single-instance only** (no
multi-node yet) and **compute-credit-limited** — "not a supercomputing center."
LSDB/Dask comfortable to ~1–10M rows on one large instance (e.g. 128 CPU / 64
workers). → **Batch, don't naively fan out 10^6.** This is a strong vote for a
**bounded-footprint v1**. Checkpoint every stage to Parquet (partial failures are
expected at scale).

## 5. Variability metrics & candidate criteria

Literature-calibrated thresholds (implemented in `src/selection.py`):

- **Extreme-variability quasar:** |Δg| > 1 mag over long baseline (Rumbaugh 2018; Ren 2022).
- **Mid-IR outburst (MIRONG):** ΔW1 or ΔW2 ≥ 0.5 mag vs. quiescence, >5σ.
- **Mid-IR CLAGN (Sheng 2020):** ΔW1/W2 > 0.4 mag, *both* bands → higher purity.
- **AGN mid-IR color:** W1−W2 ≥ 0.8 (Stern 2012) / >0.5 deep (Assef 2013). The
  **color crossing ~0.5 toward/away-from AGN-like tracks the transition** — the
  CLAGN-specific discriminant. Track it in **both directions**.
- **Structure function:** SF(Δt)=SF_∞[1−e^(−Δt/τ)]^½ (MacLeod 2010); CLAGN in high-SF_∞ tail.
- **Normalized excess variance:** σ²_NXS=(S²−⟨σ²_err⟩)/⟨x⟩²; flag >3σ.
- **Monotonic trend test:** Spearman of mag vs. time (sustained transition vs. stochastic).
- **Cross-band coherence:** require mid-IR event with an optical counterpart at the
  expected **dust-reverberation lag** (mid-IR lags optical by months) — strongest
  contaminant killer and a genuine selection axis.

**Contaminant discriminant (critical):** TDEs/ANTs redden in W1−W2 *faster* than
CLAGN (You et al. 2025). Bake multi-epoch MIR color tracks into selection.

**Engage Ren et al. 2022 (14,012 EVQs):** they argue CLQs are the tail of normal
quasar variability. The selection function must answer "where is the line?"

Thresholds calibrated by **injection-recovery**, not chosen by hand (§7).

## 6. Vetting, tiering & confirmation

- Auto-reject: known SNe/TDEs (broker cross-match), solar-system movers, blends
  (WISE contamination + ZTF quality flags), variable stars (Gaia color/parallax).
- **Confirmation tiers:** (a) archival spectral state change = gold;
  (b) coherent multi-band variability w/ correct lag = strong candidate;
  (c) single-band = candidate. Report all three with a tier flag.
- Confirmation spectra: DESI DR1 + SDSS-V/BHM (repeat-epoch by design) ± LAMOST.
- Propose follow-up of top tier-(b) candidates as the forward-looking hook.

## 7. Deliverables

1. **Catalog paper:** variability-selected CLAGN sample + **selection function** +
   tier flags (machine-readable table). Selection function is the headline.
2. Science: turn-on/turn-off **rates**, amplitude distribution, mid-IR↔optical
   **lag distribution** (→ dust-torus sizes), placement on AGN scaling relations,
   cross-band amplitudes as mechanism discriminator.
3. Open data products (light curves, features).

## 8. Likely referee objections → mitigations

- *"Just selection effects."* → Injection-recovery; publish completeness vs.
  (Δmag, z, cadence, host brightness).
- *"Contaminants inflate counts."* → lag-coherence cut + You et al. 2025 MIR-color
  discriminant + explicit cross-matches; quote contamination from spectroscopic spot-checks.
- *"Mid-IR variability ≠ state change."* → tie to optical/X-ray; report W1−W2 evolution.
- *"Already done (López-Navas 2023 / Yang 2024)."* → differentiate on
  all-sky / both-direction / characterized selection function / southern sky.
- *"eROSITA coverage partial."* → X-ray as corroboration only; quantify the sub-sample.

## 9. Milestones

1. **Footprint + parent sample** assembled and masked.
2. **Pipeline validated on known CLAGN** (`01_smoke_test.ipynb`) — *critical early gate.*
3. Full-sample light-curve build + feature extraction (`scale_up`, batched).
4. Candidate selection + injection-recovery selection function.
5. Vetting + tiering.
6. Write-up.

## 10. Open decisions

- **v1 scope:** bounded footprint (recommended — clean selection function, fits
  compute credits) vs. all-sky. Let the smoke test inform final call.
- **Slot-5 smoke-test object:** pin a specific Sheng 2020 / Yang 2024 mid-IR-selected
  CLAGN with coordinates (see `src/smoke_test_targets.py` TODO).
- **Compute-credit budget:** estimate from smoke-test runtime × sample size.

## Key references

- Ricci & Trakhtenbrot 2023 (review): arXiv:2211.05132
- López-Navas et al. 2023 (tri-band, key competitor): arXiv:2306.13808
- Yang et al. 2024 (70 turn-on, joint IR+optical): arXiv:2408.16183
- Guo et al. 2025 (DESI II, 561 CLAGN): doi 10.3847/1538-4365/adc124
- Zeltyn et al. 2024 (SDSS-V, 116): arXiv:2401.01933
- Ren et al. 2022 (14,012 EVQs): arXiv:2111.07057
- Jiang/Wang MIRONG 2021: arXiv:2012.06806
- Sheng et al. 2020 (mid-IR CLAGN pilot): arXiv:1905.02904
- You et al. 2025 (MIR color TDE vs CLAGN): arXiv:2503.10053
