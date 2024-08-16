import streamlit as st
import time
from code_editor import code_editor

from CodeEditor import defaut_btn_setting

import json
from code_editor import code_editor
from streamlit_echarts import st_echarts
import random
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="PsyAgent",
    page_icon="🐦"
)
# Function to initialize session state
# Vendor webfront text for instruction
st.title("PsyAgent")
st.subheader("Empowering counseling with large language models.")

st.sidebar.title("Dashboard")
# Sidebar with parameters
mode = st.sidebar.radio('Select Mode', ['Debug', 'Prod'], index=0)

# 
def agent_parameters_on_change():
    agent = st.session_state["Agents"]["agent"]
    agent.update_params(temperature=temperature, max_tokens=max_token_length, top_p=top_p)
    
# Sidebar with parameters
max_token_length = st.sidebar.slider('max_length', 0, 4096, 3000, step=1,on_change=agent_parameters_on_change,help="The maximum length of tokens.")
top_p = st.sidebar.slider('top_p', 0.0, 1.0, 0.6, step=0.01,on_change=agent_parameters_on_change,help="The nucleus sampling probability.")
temperature = st.sidebar.slider('temperature', 0.0, 1.0, 0.95, step=0.01,on_change=agent_parameters_on_change,help="The temperature for sampling.")
sql_timeout = st.sidebar.slider('SQL_timeout', 0, 100, 10, step=1,help="The timeout for SQL queries. (Invalid)")
st.sidebar.subheader("""Magic commands include:\n **\$run**: run PGSQL code \n **\$explain** : explain SQL result\n **\$visulize**： Draw chart of data""")
st.sidebar.code("""  """)
st.sidebar.code("""Emotion Classsification""")
st.sidebar.code("""Strategy Classification""")
st.sidebar.code("""Suggested Psychotherapy""")
messages_container = st.container()

# def edit_code(origin_code:str):

if "code_editor" in st.session_state and st.session_state["code_editor"]['type']!='':
    print(st.session_state["code_editor"],"Code editor in streamlit is not a shit!!!")

# initialize sesssion_state (run first)
print("Initializing session_state, loading ...")
# Initialize session state variables if they don't exist
if "target" not in st.session_state:
    st.session_state["target"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []
else:# 有历史则刷历史
    flash_dialog_history(history=st.session_state["history"])
if "gen_json" not in st.session_state:
    st.session_state["gen_json"] = []


# Sidebar with parameters
@st.cache_resource
def initialize_st():
    print("Initializing page, loading Agent...")
    agent = Agent()
    
    if "target" in st.session_state and st.session_state["target"] is not None:
        target = st.session_state["target"]
        print("--- target ", target)
        agent.change_prompt(target)
    
    agentVisual = AgentVisual() # Agent for echart
    formatter = Formatter() # format resul/t decode/encode for GPT input/ouput
    print("Agent loaded")
    return {"agent": agent, "formatter": formatter,"agentVisual":agentVisual}

# Load Agents with a spinner
with st.spinner("Loading Agents, please wait..."):
    st.session_state["Agents"] = initialize_st()

# Radio button to select target
selected_target=st.sidebar.radio(
    "Select target for code generation",
    ["dau", "miniapp"],
    captions=["E.g., Bing APP DAU in the last 10 days.", "What is the highest DAU Miniapp in Bing APP?"],
    help="Analysis target for code"
)

