import plotly.graph_objects as go


def plotly_interactive_paths(turn_points: dict,
                             central_port: tuple,
                             knot: tuple = None,
                             title: str = 'Wire paths',
                             central_port_size: int = 10
                             ):
    fig = go.Figure()

    # Plot the wire paths
    for wire_id in turn_points.keys():
        path = turn_points[wire_id]

        fig.add_trace(
            go.Scatter(
                x=path['x'],
                y=path['y'],
                name=wire_id,))

        fig.update_layout(
            title=title,
            xaxis_title='X',
            yaxis_title='Y',
        )

    # Add the central port
    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=[central_port[0]],
            y=[central_port[0]],
            marker=dict(size=central_port_size),
            showlegend=False
        )
    )

    # Add extra point if required
    if knot is not None:
        fig.add_trace(
            go.Scatter(
                mode='markers',
                x=[knot[0]],
                y=[knot[1]],
                marker=dict(size=central_port_size),
                name='Closest knot'
            )
        )

    return fig
