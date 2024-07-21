import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="DataJarvis",
    page_icon=":robot:"
)


# Function to initialize session state

# Vendor webfront text for instruction
# st.title("Data-Jarvis")
# st.subheader("Empowering data with large language models.")
with open("./docs/Tutorial.md", encoding='utf-8', errors='ignore') as file:
    st.write(file.read())