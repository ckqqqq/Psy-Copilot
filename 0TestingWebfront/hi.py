import streamlit as st
import pandas as pd
import numpy as np
st.text('Fixed width text')
st.markdown('_Markdown_') # see #*
st.caption('Balloons. Hundreds of them...')
st.latex(r''' e^{i\pi} + 1 = 0 ''')
st.write('Most objects') # df, err, func, keras!
st.write(['st', 'is <', 3]) # see *
st.title('My title')
st.header('My header')
st.subheader('My sub')
st.code('for i in range(8): foo()')


data=pd.DataFrame(data={
    'ID': np.arange(1, 11),
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva', 'Frank', 'Grace', 'Hannah', 'Ian', 'Julia'],
    'Age': np.random.randint(18, 65, 10),
    'Height': np.random.uniform(1.5, 2.0, 10),
    'IsStudent': np.random.choice([True, False], 10),
    'Score': np.random.uniform(50, 100, 10)
})
# Show different content based on the user's email address.

st.button('Hit me')
st.data_editor(data)
st.checkbox('Check me out')
st.radio('Pick one:', ['nose','ear'])
st.selectbox('Select', [1,2,3])
st.multiselect('Multiselect', [1,2,3])
st.slider('Slide me', min_value=0, max_value=10)
st.select_slider('Slide to select', options=[1,'2'])
st.text_input('Enter some text')
st.number_input('Enter a number')
st.text_area('Area for textual entry')
st.date_input('Date input')
st.time_input('Time entry')
uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
st.camera_input("一二三,茄子!")
st.color_picker('Pick a color')
for uploaded_file in uploaded_files:
    st.write("filename:", uploaded_file.name)
    # st.write(bytes_data)

# st.download_button(label="hi",data=data)
# * optional kwarg unsafe_allow_html = True