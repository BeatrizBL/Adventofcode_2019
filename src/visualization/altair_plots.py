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
                 sorting = None,
                 legend_visible: bool = True,
                 xlims: tuple = None,
                 ylims: tuple = None
                 ):

    # Coloring column
    if sorting is not None:
        if legend_visible is True:
            color = alt.Color(color_column+':N', sort=sorting)
        else:
            color = alt.Color(color_column+':N', sort=sorting, legend=None)
    else:
        if legend_visible is True:
            color = alt.Color(color_column+':N')
        else:
            color = alt.Color(color_column+':N', legend=None)

    # Size of the dots
    if size is None:
        size = 5000/max(data[x_column].max(), data[y_column].max())

    # Axis limits
    if xlims is None:
        xlims = (int(data[x_column].min()), int(data[x_column].max()))
    if ylims is None:
        ylims = (int(data[y_column].min()), int(data[y_column].max()))

    chart = alt.Chart(data).mark_circle(size=size).encode(
        x=alt.X(x_column+':Q', scale=alt.Scale(domain=(xlims[0], xlims[1]))),
        y=alt.Y(y_column+':Q', scale=alt.Scale(domain=(ylims[0], ylims[1]))),
        color=color
    )
    return chart
