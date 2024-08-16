from typing import ItemsView
import streamlit as st
import time
from code_editor import code_editor


from CodeEditor import defaut_btn_setting

import json
from streamlit_echarts import st_echarts
import random
from datetime import datetime
from src.Agent import Agent
from src.Formatter import Formatter
from src.utils.common_function import save_file

import os
from dotenv import load_dotenv


options={
  "xAxis": {
    "type": 'category',
    "data": ['Happy', 'Angry', 'Sad', 'Hate', 'Neutral', 'Surprise', 'Affection']
  },
  "yAxis": {
    "type": 'value'
  },
  "series": [
    {
      "data": [120, 200, 150, 80, 70, 110, 130],
      "type": 'bar'
    }
  ]
}


# 加载.env文件中的环境变量
load_dotenv()
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
# mode = st.sidebar.radio('Select Mode', ['Debug', 'Prod'], index=0)

# 
def agent_parameters_on_change():
    agent = st.session_state["Agents"]["agent"]
    agent.update_params(temperature=temperature, max_tokens=max_token_length, top_p=top_p)
def delete_question():
    pass
# Sidebar with parameters
max_token_length = st.sidebar.slider('max_length', 0, 4096, 3000, step=1,on_change=agent_parameters_on_change,help="The maximum length of tokens.")
top_p = st.sidebar.slider('top_p', 0.0, 1.0, 0.6, step=0.01,on_change=agent_parameters_on_change,help="The nucleus sampling probability.")
temperature = st.sidebar.slider('temperature', 0.0, 1.0, 0.95, step=0.01,on_change=agent_parameters_on_change,help="The temperature for sampling.")
sql_timeout = st.sidebar.slider('SQL_timeout', 0, 100, 10, step=1,help="The timeout for SQL queries. (Invalid)")


def flash_dialog_history(history):
    pass
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
if "echart_flash_page_cnt" not in st.session_state:
    st.session_state["echart_flash_page_cnt"]=0

# Sidebar with parameters
@st.cache_resource
def initialize_st():
    print("Initializing page, loading Agent...")
    agent = Agent()
    
    if "target" in st.session_state and st.session_state["target"] is not None:
        target = st.session_state["target"]
        print("--- target ", target)
    
    # agentExplain = AgentExplain() # Agent for explain SQL result
    # agentVisual = AgentVisual() # Agent for echart
    # toolPGSQL=None
    # toolPGSQL = ToolPGSQL() # Agent for run PGSQL
    # agentToolUser= AgentToolUser()
    formatter = Formatter() # format result decode/encode for GPT input/ouput
    print("Agent loaded")
    return {"agent": agent,"formatter": formatter}

st.session_state['suggested_response']="stupid_guy"
# Load Agents with a spinner
with st.spinner("Loading Agents, please wait..."):
    st.session_state["Agents"] = initialize_st()

# Radio button to select target
# selected_target=st.sidebar.radio(
#     "Select target for code generation",
#     ["dau", "miniapp"],
#     captions=["E.g., Bing APP DAU in the last 10 days.", "What is the highest DAU Miniapp in Bing APP?"],
#     help="Analysis target for code"
# )
# if "target" in st.session_state and selected_target!=st.session_state["target"]:
#     st.session_state["target"]=selected_target
#     st.sidebar.write(f"Analysis target updated to: {selected_target}")
    # st.session_state["Agents"]["agent"].change_prompt(st.session_state["target"])
#     st.sidebar.write(st.session_state['target'])
def get_single(item):
    st.write(item)
tab1, tab2 = st.tabs(["Single Table Operation", "Double Table Operation"])


def flash_dialog():
    with right_container.chat_message("assistant"):
        right_container.write("dkfjasdlkfjldskajflksdajfldksajf")
    with right_container.chat_messages("user"):
        st.write("test")

with tab1:
    left_column, right_column = st.columns(2, gap = "large")
    with left_column:
        
        st_echarts(options=options,key=str(st.session_state["echart_flash_page_cnt"]))
        illustration0 = st.markdown('- We will provide you a backgound and a case for counseling.\n\n - You can also upload your own file containing backgound and case history for counseling.\n\n')
        # 使用 - 是分点陈列的关键
        uploadFile = st.file_uploader("Upload case record if here", type=["csv", "xlsx", "xls", "docx"], on_change=delete_question)

        title_column = st.columns(3, gap = "large")
        text_prompt = st.empty()
        with title_column[0]:
            table_title = st.markdown('###### Provided case:')
        with title_column[2]:
            refresh_button = st.button("🔄 Refresh File", key = "refresh table button", use_container_width=True)
            if refresh_button:
                if st.session_state['table0']["uploadFile"] is None:
                    # uploadFile = None
                    table, df, file_detail, questions, chat_mode = get_single(last_table=st.session_state['table0']['table'])
                    st.session_state['table0'] = {
                        "uploadFile": None,
                        "table": table,
                        "dataframe": df,
                        "file_detail": file_detail,
                    }
                    st.session_state['questions'] = questions
                    st.session_state['chat_mode'] = chat_mode
                    st.rerun()
                else:
                    text_prompt.info("Please delete the uploaded file before getting a new default table.")
                    time.sleep(1)
                    text_prompt.text("")

        if uploadFile is not None:
            if uploadFile == st.session_state['table0']['uploadFile']:
                st.dataframe(st.session_state['table0']['dataframe'], height=min(500, len(st.session_state['table0']['dataframe'])*50), use_container_width=True)
            else:
                try:
                    # if upload csv or xlsx, use Code mode
                    if uploadFile.name.endswith(('.csv', '.xlsx')):
                        st.session_state['chat_mode'] = 'Code'
                    elif uploadFile.name.endswith(('.docx')):
                        st.session_state['chat_mode'] = 'QA'

                    # save file
                    with st.spinner('loading...'):
                        df, tabular, file_detail = save_file(uploadFile)
                        st.session_state['table0'] = {
                            "uploadFile": uploadFile,
                            "table": tabular,
                            "dataframe": df,
                            "file_detail": file_detail
                        }
                        # generate questions
                        questions = []
                        
                    st.session_state['questions'] = questions
                    st.dataframe(df, height=min(500, len(df)*50), use_container_width=True)
                    st.session_state['chat']['user_input_single'] = None
                    st.session_state['chat']['bot_response_single_1'] = None
                    st.session_state['chat']['bot_response_single_2'] = None

                    # st.session_state['questions'] = []
                except Exception as e:
                    # print(str(e))
                    st.text("Error Saving File")
                st.rerun()
        elif "question" in st.session_state and st.session_state['questions'] is not None:
            df = st.session_state['table0']['dataframe']
            st.dataframe(df, height=min(500, len(df)*50), use_container_width=True)
        else:
            st.session_state['table0'] = {"uploadFile": None, "table": None, "dataframe": None, "file_detail": None} 
    with right_column:
        right_container = st.container()
        human_input = st.text_input(label="query",value=st.session_state['suggested_response'])
        if human_input:
            # 
            st.session_state['suggested_response']=human_input
            st.write(st.session_state['suggested_response'])
            with st.spinner("""AI is generating databases, and explaining results... \n
                            ❤ Thank you for your patience. """):
                with right_container.chat_message("assistant"):
                    st.write("text")