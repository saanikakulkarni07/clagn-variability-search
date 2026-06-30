"""Variability metrics and literature-calibrated CLAGN selection thresholds.

These are the stage-3 selection criteria from PLAN.md section 5. Thresholds here
are LITERATURE PRIORS — the final cuts must be calibrated by injection-recovery
(PLAN.md section 7), not frozen at these values.

References are inline. Functions operate on simple (time, mag, mag_err) arrays so
they can be mapped over per-object/per-band light curves in the feature-extraction
stage.
"""

from __future__ import annotations

import numpy as np

# --- Literature thresholds (priors; recalibrate via injection-recovery) ---

THRESHOLDS = {
    # Extreme-variability quasar, optical (Rumbaugh+2018; Ren+2022)
    "delta_g_evq": 1.0,            # |Delta g| > 1 mag over a long baseline
    # Mid-IR outburst (MIRONG; Jiang/Wang 2021)
    "delta_w_mirong": 0.5,         # ΔW1 or ΔW2 >= 0.5 mag vs quiescence
    # Mid-IR CLAGN, both bands for purity (Sheng+2020)
    "delta_w_clagn": 0.4,          # ΔW1 AND ΔW2 > 0.4 mag
    # AGN mid-IR color (Stern+2012 / Assef+2013); transition tracked by crossing
    "wise_color_agn": 0.8,         # W1-W2 >= 0.8 -> AGN-like (0.5 for deep)
    "wise_color_transition": 0.5,  # crossing ~0.5 (either direction) flags a transition
    # Normalized excess variance significance flag (Nandra+1997; Vaughan+2003)
    "nxs_sigma": 3.0,
}


def delta_mag(mag: np.ndarray) -> float:
    """Peak-to-trough amplitude (robust to outliers via 5th/95th percentiles)."""
    mag = np.asarray(mag, float)
    mag = mag[np.isfinite(mag)]
    if mag.size < 2:
        return np.nan
    return float(np.percentile(mag, 95) - np.percentile(mag, 5))


def normalized_excess_variance(mag: np.ndarray, mag_err: np.ndarray) -> float:
    """sigma^2_NXS = (S^2 - <sigma_err^2>) / <x>^2  (Vaughan+2003).

    Note: computed in magnitudes here for convenience; convert to flux for
    publication-grade values. Returns NaN if undersampled.
    """
    mag = np.asarray(mag, float)
    err = np.asarray(mag_err, float)
    good = np.isfinite(mag) & np.isfinite(err)
    mag, err = mag[good], err[good]
    if mag.size < 3:
        return np.nan
    mean = mag.mean()
    s2 = mag.var(ddof=1)
    return float((s2 - np.mean(err ** 2)) / mean ** 2)


def monotonic_trend(time: np.ndarray, mag: np.ndarray) -> float:
    """Spearman rank correlation of mag vs time.

    |rho| near 1 => sustained transition (turn-on/turn-off); near 0 => stochastic.
    Sign distinguishes direction. Uses scipy if available, else a numpy fallback.
    """
    time = np.asarray(time, float)
    mag = np.asarray(mag, float)
    good = np.isfinite(time) & np.isfinite(mag)
    time, mag = time[good], mag[good]
    if time.size < 4:
        return np.nan
    try:
        from scipy.stats import spearmanr
        rho, _ = spearmanr(time, mag)
        return float(rho)
    except Exception:
        # Pearson on ranks as a fallback
        rt = np.argsort(np.argsort(time))
        rm = np.argsort(np.argsort(mag))
        return float(np.corrcoef(rt, rm)[0, 1])


def wise_color_change(w1: np.ndarray, w2: np.ndarray) -> float:
    """Change in W1-W2 color across the baseline (early-epoch vs late-epoch median).

    Positive => reddening toward AGN-like (possible turn-on);
    negative => bluing away from AGN-like (possible turn-off).
    CAUTION: TDEs/ANTs redden FASTER than CLAGN (You+2025) — use the multi-epoch
    color *track*, not just the endpoints, to separate them.
    """
    w1 = np.asarray(w1, float)
    w2 = np.asarray(w2, float)
    color = w1 - w2
    good = np.isfinite(color)
    color = color[good]
    if color.size < 4:
        return np.nan
    n = max(2, color.size // 4)
    return float(np.median(color[-n:]) - np.median(color[:n]))


def is_candidate(features: dict) -> bool:
    """Apply the prior thresholds to a per-object feature dict.

    `features` should contain keys like: delta_w1, delta_w2, delta_g,
    wise_color_change, nxs_significance. Missing keys are treated as non-passing.
    This is a PRIOR filter for the smoke test / first pass — the production
    selection is the injection-recovery-calibrated, multi-dimensional version.
    """
    t = THRESHOLDS
    mir = (features.get("delta_w1", 0) > t["delta_w_clagn"]
           and features.get("delta_w2", 0) > t["delta_w_clagn"])
    opt = abs(features.get("delta_g", 0)) > t["delta_g_evq"]
    color = abs(features.get("wise_color_change", 0)) > 0.2
    # CLAGN-like: a mid-IR transition with corroborating color change, OR a
    # strong optical EVQ-level event. (Cross-band lag-coherence added in stage 4.)
    return (mir and color) or opt
