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


def scatter_plot(data: pd.DataFrame,
                 x_column: str = 'x',
                 y_column: str = 'y',
                 color_column: str = 'value',
                 size: int = None,
                 sorting = None
                 ):

    # Coloring column
    if sorting is not None:
        color = alt.Color(color_column+':N', sort=sorting)
    else:
        color = alt.Color(color_column+':N')

    # Size of the dots
    if size is None:
        size = 5000/max(data[x_column].max(), data[y_column].max())

    chart = alt.Chart(data).mark_circle(size=size).encode(
        x=x_column+':Q',
        y=y_column+':Q',
        color=color
    )
    return chart
