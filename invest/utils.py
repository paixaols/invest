import pandas as pd


def qs_to_df(queryset):
    q = queryset.values()
    df = pd.DataFrame.from_records(q)
    return df
