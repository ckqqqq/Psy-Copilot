# from transformers import AutoModel, AutoTokenizer
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from streamlit_chat import message
from Agent import Agent
from ToolPGSQL import ToolPGSQL
from Formatter import Formatter
from AgentExplain import AgentExplain


# import torch
# from peft import AutoPeftModelForCausalLM
# from transformers import AutoTokenizer, pipeline
# streamlit run text_2_SQL_web_demo.py --server.port 11234
st.set_page_config(
    page_title="DataCopilot",
    page_icon=":robot:"
)

@st.cache_resource
def initialize_st():
    print("页面初始化，载入Agent..")
    agent=Agent()
    agentExplain=AgentExplain()
    toolPGSQL=ToolPGSQL()
    formatter=Formatter()
    print("载入Agent Done")
    return {"agent":agent,"toolPGSQL":toolPGSQL,"agentExplain":agentExplain,"formatter":formatter}

MAX_TURNS = 30
MAX_BOXES = MAX_TURNS * 2


def codeGenerate(human_input,messages):
    """Main chat part"""
    Agents = st.session_state["Agents"]
    agent,toolPGSQL,formatter,agentExplain = Agents["agent"],Agents["toolPGSQL"],Agents["formatter"],Agents["agentExplain"]
    messages.chat_message("user").write(human_input)
    messages.chat_message("assistant").write(f"Echo: {human_input}")
    return messages

# def excute_code():
#     pass
messages = st.container(height=300)
if prompt := st.chat_input("Say something"):
    messages.chat_message("user").write(prompt)
    messages.chat_message("assistant").write(f"Echo: {prompt}")

st.title("Data-Jarvis")
# st.write("""## Data-Copilot """)

container = st.container()
# SCHEMA
# create a prompt text for the text generation


with st.spinner("Loading Agents，请稍等........ Agents is loading......"):
    # text generation
    st.session_state["Agents"] = initialize_st()

# st.write("""####  请大家帮忙想一个很酷的名字 例如 Data-Jarvis""")
st.header("""Code Agent""")
# st.subheader("""This is a SQL Agent that can help you generate SQL queries based on your questions.""")
# st.write("""Please input the query. [e.g,. How many markets do we have?]: """)
# schema_text = st.text_area(label="请用英文输入表格格式，请大写SQL关键字(Please input the table format in English, using uppercase SQL keywords. )，例如: ",
#             height = 100,
#             placeholder="SCHEMA:\nCREATE TABLE table_name_23 (country VARCHAR, _percentage_change_on_year VARCHAR, rank VARCHAR)")

prompt_text = st.text_area(label="请输入需要查询data的问句? [eg,. 我们有几个market? / How many markets do we have?] : ",
            height = 100,
            placeholder=r"Bing APP一天有多少用户?")

max_length = st.sidebar.slider(
    'max_length', 0, 4096, 2048, step=1
)
top_p = st.sidebar.slider(
    'top_p', 0.0, 1.0, 0.6, step=0.01
)
temperature = st.sidebar.slider(
    'temperature', 0.0, 1.0, 0.95, step=0.01
)
sql_timeout = st.sidebar.slider(
    'SQL_timeout', 0, 100, 10, step=1
)
if 'state' not in st.session_state:
    st.session_state['state'] = []
    # 简单来讲就是对话历史

if st.button("发送 Submit", key="predict"):
    with st.spinner("AI正在思考，请稍等........ AI is thinking......"):
        # text generation
        st.session_state["state"] = codeGenerate(prompt_text, messages)

# st.header("""SQL Executor""")
# st.subheader("""This is a SQL Executor that can help you run SQL codes based on your questions.""")

prompt_text = st.text_area(label="SQL Executor ",
            height = 100,
            placeholder=r"Bing APP一天有多少用户?")

if st.button("执行 Execute", key="Execute"):
    with st.spinner("SQL正在执行，请稍等........ SQL is running......"):
        # text generation
        st.session_state["state"] = codeGenerate(prompt_text,messages)