"""
standard errors and 95% confidence intervals for the 2004 -> 2024 change in
hours per week, boys/men 15-24, for each activity category in 5_final.ipynb

    inputs:
    ______

        data/processed/0324/atussum-0324.parquet
        data/processed/0324/atusact-0324.parquet
        data/processed/0324/atuswgts-0324.parquet   (BLS replicate weights)

    outputs:
    _______

        data/processed/nb_6_standard_errors_boys_15-24.csv

uses BLS's successive difference replication: each estimate is recomputed with each
of the 160 replicate weights, and

    Var = 4/160 * sum_r (estimate_r - estimate)^2

the SE of the change uses the replicate differences (2024_r - 2004_r) directly.
"""

from math import erfc, sqrt

import numpy as np
import pandas as pd

from atus_utils import PROCESSED, load_table, code_social_activities

YEARS = [2004, 2024]
MAX_AGE = 25
SEX = 1  # TESEX: 1 = male

REPS = [f"TUFNWGTP{i:03d}" for i in range(1, 161)]

# READ IN THE FILES

summ = load_table("sum", ["TUCASEID", "TUYEAR", "TEAGE", "TESEX", "TUFNWGTP"])
sample = summ[(summ.TESEX == SEX) & (summ.TEAGE < MAX_AGE) & summ.TUYEAR.isin(YEARS)]

# 2004 and 2024 only, so TUFNWGTP is the right weight (the 2020 fix in add_weight doesn't apply)
wgts = load_table("wgts", ["TUCASEID"] + REPS)
sample = pd.merge(sample, wgts, on="TUCASEID", how="left", validate="1:1")
assert sample[REPS].notna().all().all(), "respondents missing replicate weights"

act = load_table("act", ["TUCASEID", "TUACTDUR24", "TRCODEP", "TRTIER2P"])
act = act[act.TUCASEID.isin(sample.TUCASEID)].copy()
act["description"] = code_social_activities(act)

# minutes per day in each category, one row per respondent -- zero if they didn't do it
minutes = act.pivot_table(index="TUCASEID", columns="description", values="TUACTDUR24", aggfunc="sum")
minutes = minutes.reindex(sample.TUCASEID).fillna(0)


def hours_per_week(year, weight_col):
    """weighted average hours per week for every category, same estimator as weighted_average_pivot"""

    in_year = (sample.TUYEAR == year).values
    w = sample.loc[in_year, weight_col].values

    return (minutes.values[in_year] * w[:, None]).sum(axis=0) / w.sum() * 7 / 60


def sdr_se(estimate, replicates):
    return np.sqrt(4 / len(REPS) * ((replicates - estimate) ** 2).sum(axis=0))


est = {year: hours_per_week(year, "TUFNWGTP") for year in YEARS}
reps = {year: np.array([hours_per_week(year, r) for r in REPS]) for year in YEARS}

change = est[2024] - est[2004]
se_change = sdr_se(change, reps[2024] - reps[2004])

results = pd.DataFrame({
    "description": minutes.columns,
    "hrs_2004": est[2004],
    "se_2004": sdr_se(est[2004], reps[2004]),
    "hrs_2024": est[2024],
    "se_2024": sdr_se(est[2024], reps[2024]),
    "change": change,
    "se_change": se_change,
    "ci95_low": change - 1.96 * se_change,
    "ci95_high": change + 1.96 * se_change,
})
results["p"] = [erfc(abs(c / s) / sqrt(2)) for c, s in zip(change, se_change)]
results = results.sort_values("change", ascending=False)

# sanity check: categories cover the whole week
for year in YEARS:
    assert abs(est[year].sum() - 168) < 1e-6

print("n:", sample.groupby("TUYEAR").size().to_dict())
print(results.round(3).to_string(index=False))

results.to_csv(PROCESSED / f"analysis_6_standard_errors_boys_15-{MAX_AGE - 1}.csv", index=None)
