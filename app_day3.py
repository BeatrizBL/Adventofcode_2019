import streamlit as st
import os
from src import day3
from src.visualization import wire_paths

# Side bar settings
st.sidebar.markdown('### Settings')
root_path = st.sidebar.text_input(label='Data folder:', value='data/raw/day3')
wire_file = st.sidebar.text_input(label='Wires file:', value='wires.txt')

# Main app
st.title('Day 3: Crossed Wires')
'#'

'#### Current working directory'
st.info(os.getcwd())

'#### Data access'
path = os.path.join(root_path, wire_file)
if os.path.exists(root_path):
    st.info('Data folder available.')

    # Check the wire file
    try:
        f = open(path, 'r')
        wires = f.readlines()
        st.info('Wire file available.')

        # Execution
        if st.button('Go!'):

            '## Part 1'

            # Format wires lists
            wires = [w.replace('\n', '') for w in wires]
            wires = [w.split(',') for w in wires]

            try:
                # Get maximum dimensions
                dims = [day3.get_panel_dimension(w) for w in wires]
                dim = 2*max(dims)+1
                central_port = (max(dims), max(dims))

                try:
                    # Get the wire matrices
                    full_matrix = None
                    turn_points = {}
                    central_port_id = len(wires)+1

                    i = 0
                    for w in wires:
                        i = i+1
                        res = day3.get_wire_path(
                            w,
                            size_x=dim, size_y=dim,
                            central_port=central_port,
                            central_port_id=central_port_id
                        )

                        # Add current wire to the complete matrix
                        if full_matrix is None:
                            full_matrix = res['matrix']
                        else:
                            full_matrix = full_matrix + res['matrix']

                        # Add current wire to turning points
                        turn_points.update(
                            {'Wire '+str(i): res['turn_points']})

                    try:
                        # Get closest point
                        dist_res = day3.get_minimum_Manhattan(
                            full_matrix,
                            knot_id=len(wires)
                        )

                        try:
                            # Plot wire paths with closest knot
                            fig = wire_paths.plotly_interactive_paths(
                                turn_points,
                                central_port=central_port,
                                knot=dist_res['position']
                            )
                            st.plotly_chart(fig)

                            st.markdown(
                                'Minimum Manhattan distance: {}'.format(dist_res['distance']))

                            '## Part 2'

                            try:
                                res_part2 = day3.get_minimum_combined_steps(
                                    wires,
                                    size_x=dim, size_y=dim,
                                    central_port=central_port,
                                    matrix=full_matrix,
                                    knot_id=len(wires)
                                )

                                # Plot wire paths with closest knot
                                fig = wire_paths.plotly_interactive_paths(
                                    turn_points,
                                    central_port=central_port,
                                    knot=res_part2['position']
                                )
                                st.plotly_chart(fig)

                                st.markdown(
                                    'Minimum combined steps: {}'.format(res_part2['distance']))

                            except Exception as e:
                                st.error(
                                    'Error computing minimum combined steps! {}'.format(e))

                        except Exception as e:
                            st.error(
                                'Error while plotting the wire paths! {}'.format(e))

                    except Exception as e:
                        st.error(
                            'Error computing the Manhattan distance! {}'.format(e))

                except Exception as e:
                    st.error('Error creating wire matrices! {}'.format(e))

            except Exception as e:
                st.error('Error processing the wire paths! {}'.format(e))

    except:
        st.error('Wire file not avaiable in specified folder.')
else:
    st.error('Problem in data folder check.')
