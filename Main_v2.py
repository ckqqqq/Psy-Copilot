import streamlit as st
pg = st.navigation([
    st.Page("Homepage.py", title="Homepage", icon="🐦"),
    st.Page("About.py", title="About", icon="🦥"),
],position="siderbar")
pg.run()
