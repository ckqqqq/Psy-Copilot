# from transformers import AutoModel, AutoTokenizer
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
def initialize_st(key):
    print("Initializing page, loading Agent..")
    agent = Agent(key=key)
    agentExplain = AgentExplain()
    toolPGSQL = ToolPGSQL()
    formatter = Formatter()
    print("Agent loaded")
    return {"agent": agent, "toolPGSQL": toolPGSQL, "agentExplain": agentExplain, "formatter": formatter}


MAX_TURNS = 30
MAX_BOXES = MAX_TURNS * 2


def codeGenerate(human_input,max_length, top_p, temperature, history=None):
    """Main chat part"""
    Agents = st.session_state["Agents"]
    agent,toolPGSQL,formatter,agentExplain = Agents["agent"],Agents["toolPGSQL"],Agents["formatter"],Agents["agentExplain"]
    if history is None:
        history = []
    with container:
        if len(history) > 0:
            if len(history)>MAX_BOXES:
                history = history[-MAX_TURNS:]
            for i, (query, response) in enumerate(history):
                message(query, avatar_style="big-smile", key=str(i) + "_user")
                message(response, avatar_style="bottts", key=str(i))
        message(human_input, avatar_style="big-smile", key=str(len(history)) + "_user")
        st.write(f"{max_length}-{top_p}-{temperature}")
        st.write("AI正在生成SQL查找代码,生成语句需要约20s~30s:")
        with st.empty():
            print("人类输入:",human_input)
            str_query=agent.chat(human_input)
            json_query=formatter.json_decode(
                str_query,
                need_key_list=["Analysis","SQL","input","reasoning"]
                )
            sql_query=json_query["Analysis"]["SQL"]
            sql_query=formatter.schema_table_format(sql_query,err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"],
                                                schema='sapphire',table='sapphire_engagement_metrics_master')
            response_list=[sql_query]
            st.write(response_list)
            print("PGSQL运行中")
            sql_res,col_names=toolPGSQL.execute(sql_query)
            print("PGSQL运行结束")
            sql_table_str=formatter.sql_output_format(sql_res,col_names)
            response_list.append(sql_table_str)
            print("resoning")
            print(json_query["Analysis"]["reasoning"])
            print("Explain")
            AI_explain=agentExplain.explain(query=human_input,sql_result=sql_table_str)
            response_list.append(formatter.app_id_2_name(AI_explain))
            st.write(response_list)
    return history

def excute_code():
    pass


st.title("Data-Jarvis")
# st.write("""## Data-Copilot """)

container = st.container()
# SCHEMA
# create a prompt text for the text generation
    
# Add a dropdown for selecting between "dau" and "miniapp"
key_option = st.selectbox("Choose query type:", ("dau", "miniapp"))

with st.spinner("Loading Agents, please wait........ Agents are loading......"):
    # Initialize the agents with the selected key
    st.session_state["Agents"] = initialize_st(key=key_option)


# st.write("""####  请大家帮忙想一个很酷的名字 例如 Data-Jarvis""")
st.header("""Code Agent""")
st.subheader("""This is a SQL Agent that can help you generate SQL queries based on your questions.""")
st.write("""Please input the query. [e.g,. How many markets do we have?]: """)
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
        st.session_state["state"] = codeGenerate(prompt_text, max_length, top_p, temperature, history=st.session_state["state"])

st.header("""SQL Executor""")
st.subheader("""This is a SQL Executor that can help you run SQL codes based on your questions.""")

prompt_text = st.text_area(label="请输入需要查询data的问句? [eg,. 我们有几个market?]: ",
            height = 100,
            placeholder=r"Bing APP一天有多少用户?")

if st.button("执行 Execute", key="Execute"):
    with st.spinner("SQL正在执行，请稍等........ SQL is running......"):
        # text generation
        st.session_state["state"] = codeGenerate(prompt_text, max_length, top_p, temperature, history=st.session_state["state"])