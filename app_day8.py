import streamlit as st
import os
from src import day8
from src.visualization import altair_plots

# Side bar settings
st.sidebar.markdown('### Settings')
st.sidebar.markdown('#### Image file')
root_path = st.sidebar.text_input(label='Data folder:', value='data/raw/day8')
digits_file = st.sidebar.text_input(
    label='Image digits file:', value='digits.txt')

st.sidebar.markdown('#### Layers format')
n_rows = int(st.sidebar.text_input(label='Layer rows:', value=6))
n_cols = int(st.sidebar.text_input(label='Layer columns:', value=25))

# Main app
st.title('Day 8: Space Image Format')
'#'

'#### Current working directory'
st.info(os.getcwd())

'#### Data access'
path = os.path.join(root_path, digits_file)
if os.path.exists(path):
    st.info('Image file available.')

    # Execution
    if st.button('Go!'):

        try:
            # Read the image file
            img = day8.highest_amplification_signal(digits_path=digits_file,
                                                    n_rows=n_rows,
                                                    n_cols=n_cols,
                                                    root_path=root_path)

            '## Part 1'
            st.markdown('Check whether the image is corrupted')
            try:
                # Get the corruption code
                code = day8.check_corrupted_image(img)
                st.info('Corruption check code: {}'.format(code))

                '## Part 2'
                st.markdown('Decode the image')
                try:
                    decoded = day8.decode_image(img)
                    
                    # Transform image to dataframe
                    df_img = day8.image_to_dataframe(decoded)
                    chart = altair_plots.heat_map(df_img)
                    st.altair_chart(chart)

                except Exception as e:
                    st.error('Error decoding image! {}'.format(e))

            except Exception as e:
                st.error('Error getting corruption code! {}'.format(e))
                
        except Exception as e:
            st.error('Error processing the image file! {}'.format(e))

else:
    st.error('Problem in image file check.')
