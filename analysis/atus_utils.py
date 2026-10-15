"""
shared helpers for the ATUS analysis

    usage (from a notebook or script in analysis/):
    ______

        from atus_utils import PROCESSED, load_table, add_weight, code_social_activities, weighted_average_pivot

"""

from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
PROCESSED = DATA / "processed"


def load_table(name, columns=None, year="0324"):
    """read one of the ETL'd ATUS tables, e.g. load_table("sum") -> data/processed/0324/atussum-0324.parquet

    pass columns to only read what you need -- parquet only reads those columns off disk
    """

    return pd.read_parquet(PROCESSED / year / f"atus{name}-{year}.parquet", columns=columns)


def add_weight(df):
    """add a 'weight' column: TUFNWGTP, except 2020 which uses TU20FWGT

    TUFNWGTP is -1 for every 2020 respondent, so 2020 can't use it.
    df needs TUYEAR, TUFNWGTP, and TU20FWGT.
    """

    df = df.copy()

    df['weight'] = df['TUFNWGTP']
    df.loc[df['TUYEAR'] == 2020, 'weight'] = df.loc[df['TUYEAR'] == 2020, 'TU20FWGT']

    if (df['weight'] < 0).any():
        raise ValueError("negative weights after add_weight -- check TUFNWGTP / TU20FWGT")

    return df


def code_social_activities(df):
    """label each activity with one of the categories used in the final analysis

    df needs TRTIER2P and TRCODEP. returns a Series (doesn't modify df).
    """

    description = pd.Series("all other activities", index=df.index)

    # 0101 -- Sleeping
    description[df.TRTIER2P == 101] = "Sleeping"

    # 12 -- Socializing, Relaxing, and Leisure
    description[df.TRTIER2P == 1201] = "Socializing and Communicating"
    description[df.TRTIER2P == 1202] = "Attending or Hosting Social Events"
    description[df.TRCODEP == 120303] = "Television and movies"
    description[df.TRCODEP == 120304] = "Television and movies"
    description[df.TRCODEP == 120307] = "Playing games"

    # 1301 -- Participating in Sports, Exercise, or Recreation
    description[df.TRTIER2P == 1301] = "Participating in Sports, Exercise, or Recreation"

    return description


def weighted_average_pivot(df, df_resp, weight_column, year_col, other_weighted_group_cols, group_cols, agg_col):
    """weighted average hours per week of agg_col (minutes per day), by year and group

    df:       one row per activity (TUCASEID + group_cols + agg_col)
    df_resp:  one row per respondent (TUCASEID + year_col + other_weighted_group_cols + weight_column)

    the denominator is the total weight of ALL respondents in each year/group, so people who
    didn't do an activity count as zero.

    returns one row per group, one column per year, plus raw_change (2024 - 2004)
    and percent_change_ratio (note: this is the ratio 2024 / 2004, not a percent).
    """

    df = pd.merge(df, df_resp, on = 'TUCASEID', how = 'left', validate="m:1")

    # get the total of the weights by group
    weighted_group_cols = year_col + other_weighted_group_cols
    weights_by_group = df_resp.groupby(weighted_group_cols)[weight_column].agg(['sum', 'count']).reset_index()

    # get the weighted sum for each group
    groupby_cols = weighted_group_cols + group_cols
    avg_by_code = df.groupby(groupby_cols)[[agg_col, weight_column]].apply(lambda a: sum(a[agg_col] * a[weight_column]) * 7/60).reset_index()

    # merge and divide out to get the averages
    abc_w = pd.merge(avg_by_code, weights_by_group, on = weighted_group_cols, how = 'left', validate='m:1')
    abc_w['avg_min_weighted'] = abc_w[0]/abc_w['sum']

    act_avg_pivot = abc_w.pivot_table(index = group_cols + other_weighted_group_cols, columns=year_col, values='avg_min_weighted', aggfunc='mean').reset_index()
    act_avg_pivot['raw_change'] = act_avg_pivot[2024]-act_avg_pivot[2004]
    act_avg_pivot['percent_change_ratio'] = act_avg_pivot[2024] / act_avg_pivot[2004]

    return act_avg_pivot
