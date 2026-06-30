"""The 5 known CLAGN used to validate the light-curve pipeline (Milestone 2).

All are ZTF-accessible (dec >~ -28; ZTF is a northern survey) with well-documented
NEOWISE + optical changing-look events, and span BOTH directions (turn-on and
turn-off) so the smoke test exercises the full selection logic.

Coordinates are resolved by name at runtime via SIMBAD/NED (astropy
`SkyCoord.from_name`) to avoid hand-transcription errors. The `ra_deg`/`dec_deg`
fields are approximate cached fallbacks ONLY — verify against SIMBAD before relying
on them. `expected_event` is what the pipeline should recover for the test to pass.
"""

from dataclasses import dataclass


@dataclass
class CLAGN:
    name: str            # SIMBAD/NED-resolvable identifier
    direction: str       # "turn-on" | "turn-off" | "recurrent"
    ra_deg: float        # approximate fallback — VERIFY via SkyCoord.from_name
    dec_deg: float       # approximate fallback — VERIFY
    expected_event: str  # what light_curve_collector should reveal
    ref: str


TARGETS = [
    CLAGN(
        name="Mrk 1018",
        direction="turn-off",
        ra_deg=31.5666, dec_deg=-0.2914,
        expected_event="Sy1 -> Sy1.9 fade; declining optical + mid-IR over the baseline",
        ref="McElroy+2016; Husemann+2016",
    ),
    CLAGN(
        name="Mrk 590",
        direction="turn-off",
        ra_deg=33.6398, dec_deg=-0.7668,
        expected_event="dramatic multi-decade decline + partial recovery; broad lines/continuum drop",
        ref="Denney+2014",
    ),
    CLAGN(
        name="NGC 2617",
        direction="turn-on",
        ra_deg=128.9116, dec_deg=-4.0883,
        expected_event="2013 turn-on (Sy1.8 -> Sy1); optical + mid-IR brightening",
        ref="Shappee+2014",
    ),
    CLAGN(
        name="1ES 1927+654",
        direction="turn-on",
        ra_deg=292.0083, dec_deg=65.5517,
        expected_event="dramatic 2018 changing-look outburst; strong all-band event (dec +65, deep ZTF)",
        ref="Trakhtenbrot+2019; Ricci+2020",
    ),
    # --- SLOT 5: TODO pin a specific mid-IR-SELECTED CLAGN (Sheng 2020 / Yang 2024) ---
    # Purpose: test the actual DISCOVERY channel, not just bright archetypes.
    # Pick one of the 6 spectroscopically-confirmed turn-off CLAGN in Sheng+2020,
    # or a turn-on CLQ from Yang+2024, that is ZTF-accessible. Fill in real coords.
    CLAGN(
        name="TODO-midIR-selected-CLAGN",
        direction="turn-on",
        ra_deg=float("nan"), dec_deg=float("nan"),
        expected_event="mid-IR-selected transition recovered (W1-W2 color crossing ~0.5)",
        ref="Sheng+2020 / Yang+2024 — SELECT SPECIFIC OBJECT",
    ),
]


def as_source_table():
    """Return targets as a list of dicts suitable for building a sample table.

    On Fornax, resolve coordinates fresh:
        from astropy.coordinates import SkyCoord
        c = SkyCoord.from_name(t.name)   # SIMBAD/NED
    rather than trusting the cached ra_deg/dec_deg fallbacks below.
    """
    return [
        {
            "objectid": i,
            "label": t.name,
            "ra": t.ra_deg,
            "dec": t.dec_deg,
            "direction": t.direction,
        }
        for i, t in enumerate(TARGETS)
    ]
