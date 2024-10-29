from ast import main
from openai import chat
import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None
    
ROLES = ["Client","Therapist", "Admin"]

def login():
    """登陆
    """
    st.header("Log in")
    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)
    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()
def logout():
    """退出
    """
    st.session_state.role = None
    st.write(r"https://github.com/mkhorasani/Streamlit-Authenticator/tree/main")
    st.rerun()
    
role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("src/pages/settings.py", title="Settings", icon=":material/settings:")
bug_report_page=st.Page(
    "src/pages/request.py", title="Issue", icon=":material/bug_report:"
)

admin_page = st.Page(
    "src/pages/admin.py",
    title="Admin",
    icon=":material/security:",
    default=(role == "Admin"),
)


main_COT_graph_page=st.Page(
    "PsyTherapistPage.py",
    title="Admin",
    icon=":material/healing:",
    default=True
)
create_COT_graph_page=st.Page(
    "MakePage.py",
    title="Admin",
    icon=":material/person_add:"
)
about_page=st.Page(
    "AboutPage.py",
    title="About",
    icon=":material/help:"
)
# response_page=st.Page(
    
# )
page_dict = {}

graph_COT_pages=[main_COT_graph_page,create_COT_graph_page]
admin_pages=[admin_page]
# 最关键的界面


if  st.session_state.role in ["Client","Therapist", "Admin"]:
    page_dict["Graph_&_COT"] = graph_COT_pages
    page_dict["Account"]=[logout_page, settings]
    page_dict["Feedback"]=[bug_report_page]
    page_dict["About"]=[about_page]

if st.session_state.role == "Admin":
    page_dict["Admin"] = [admin_page]


# pg = st.navigation([
#     st.Page("PsyTherapistPage.py", title="Agent", icon="🦥"),st.Page("AboutPage.py", title="About", icon="🦥")],position="siderbar")
# pg.run()


if len(page_dict) > 0:
    pg = st.navigation( page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()