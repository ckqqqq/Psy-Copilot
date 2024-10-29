import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="DataJarvis",
    page_icon=":robot:",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Graph': 'http://10.110.147.66:7474/browser/',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Function to initialize session state

# Vendor webfront text for instruction
# st.title("Data-Jarvis")
# st.subheader("Empowering data with large language models.")
with open("./docs/Tutorial.md", encoding='utf-8', errors='ignore') as file:
    st.write(file.read())