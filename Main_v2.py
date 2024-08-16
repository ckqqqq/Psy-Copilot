import streamlit as st
# pg = st.navigation([
#     # st.Page("HomePage.py", title="Homepage", icon="🐦"),
#     st.Page("About.py", title="About", icon="🦥"),
#     st.Page("PsyTherapistPage.py")
# ],position="siderbar")
# pg.run()

# import streamlit as st
# from page_functions import page1

pg = st.navigation([st.Page("About.py", title="About", icon="🦥"),
    st.Page("PsyTherapistPage.py")],position="siderbar")
pg.run()
