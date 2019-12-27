import altair as alt
import pandas as pd


def heat_map(data: pd.DataFrame,
             x_column: str = 'X',
             y_column: str = 'Y',
             color: str = 'Pixels'
             ):

    chart = alt.Chart(data).mark_rect().encode(
        x=x_column+':O',
        y=y_column+':O',
        color=color+':Q'
    )
    return chart
