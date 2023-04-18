import pandas as pd


def qs_to_df(queryset, *args):
    q = queryset.values(*args)
    df = pd.DataFrame.from_records(q)
    return df
