import streamlit as st
import time
from code_editor import code_editor
# from Agent import Agent
# from ToolPGSQL import ToolPGSQL
# from Formatter import Formatter
# from AgentExplain import AgentExplain
from CodeEditor import defaut_btn_setting,test_code
import pandas as pd
import numpy as np
from pyecharts.charts import Bar
from pyecharts import options as opts
import streamlit.components.v1 as components
import json
from CodeEditor import defaut_btn_setting,test_code
from code_editor import code_editor

from pyecharts import options as opts
from pyecharts.charts import Bar
from streamlit_echarts import st_echarts
# import streamlit.components.v1 as components

options = {
    "xAxis": {
        "type": "category",
        "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
    ],
}

# 页面标题
# 页面标题
st.set_page_config(
    page_title="DataCopilot",
    page_icon=":robot:"
)
# 大标题
st.title("Data-Jarvis")

# 侧边框
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

if "history" not in st.session_state:
    st.session_state["history"] = []


    # return code_editor_response

def flash_dialog_history(history):
    for idx, h in enumerate(history):
        if h["role"] == "user":
            messages_container.chat_message("user").write(h["text"])
        if h["role"] == "assistant" and h["type"] == "reasoning":
            messages_container.chat_message("assistant").write(f"推理: {h['text']}")
        if h["role"] == "assistant" and h["type"] == "code":
           messages_container.chat_message("assistant").code(f"推理: {h['text']}")
            # messages_container.chat_message("assistant").code(h["text"],line_numbers=True,language='pgsql')
        if h["role"] == "assistant" and h["type"] == "message":
            messages_container.chat_message("assistant").write(h["text"])
    return messages_container

# @st.cache_resource(hash_funcs={dict: lambda response: response.get("id")})
# def code_editor_listener(code_editor_response):
#     if code_editor_response['type'] == 'submit':
#         st.session_state["sql_code"].append("修改后的代码")
#         print(code_editor_response['text'])
#         st.session_state["history"].append({"role": "assistant", "text": "修改后的代码", "type": "message"})
#     flash_dialog_history(history=st.session_state["history"])
#     st.write(code_editor_response)
#     time.sleep(10)
#     return code_editor_response

def code_generation(human_input, history):
    time.sleep(2)
    history.append({"role": "assistant", "text": f"推理: {human_input}", "type": "reasoning"})
    history.append({"role": "assistant", "text": f"dlkfjslkfjlsakfjlsaf", "type": "code"})
    # st.session_state["sql_code"] = st.session_state["sql_code"] + ["select * from table;"]
    # code_editor_response = code_editor(
    #     code=test_code,
    #     buttons=defaut_btn_setting,
    #     theme="dark",
    #     lang="pgsql",
    #     key="test",
    #     allow_reset=True
    # )
    # code_editor_listener(code_editor_response)
    return history

if "history" not in st.session_state:
    st.session_state["history"] = []
if "sql_code" not in st.session_state:
    st.session_state["sql_code"] = []


messages_container = st.container()

if human_input := st.chat_input("请输入你需要咨询的问题 eg., bing 的dau有多少？ "):
    st.session_state["history"].append({"role": "user", "text": human_input})
    # messages_container.chat_message("user").components.v1.html(c, width=1000, height=1000)
    with messages_container.chat_message("user"):
        st_echarts(options=options)
        # st.markdown("[hhhh](https://img-blog.csdnimg.cn)")
        with st.expander("Edit chart"):
            url="""https://echarts.apache.org/examples/"""
            st.markdown(f"Paste json and edit chart at here: {url}")
            st.code(json.dumps(options),language="json")
        
    with messages_container.chat_message("user"):
        code_editor_response = code_editor(
        code=test_code,
        buttons=defaut_btn_setting,
        theme="dark",
        lang="pgsql",
    )
        
    with messages_container.chat_message("user"):
        st.text("**abcd**dfaldskfjlkdsjf\r\ndd法撒旦范德萨发放"+"\n"+"dsfdsaf")
        st.text("""| **Check Item**         | **Link/Status**                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------- |
| **OKR - SA DAU**       | [DAU ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229619)       |
| **OKR - SA Retention** | [Retention ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229646) |
| **OKR - Codex Chat**   | [Codex ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229592)     |

""")
        
# code_handle_action(code_editor_response)
    #     st.line_chart(np.random.randn(30,3))
    #     st.components.html(c, width=1000, height=1000)
