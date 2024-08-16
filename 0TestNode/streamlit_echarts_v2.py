# import streamlit as st
# import time

# from CodeEditor import defaut_btn_setting,test_code
# import pandas as pd
# import numpy as np
# # from pyecharts.charts import Bar
# # from pyecharts import options as opts
# import streamlit.components.v1 as components
# import json
# from CodeEditor import defaut_btn_setting,test_code


from streamlit_echarts import st_echarts
import streamlit as st
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



def flash_dialog_history(history):
    for idx, h in enumerate(history):
        if h["role"] == "user":
            messages_container.chat_message("user").write(h["text"])
        if h["role"] == "assistant" and h["type"] == "reasoning":
            messages_container.chat_message("assistant").write(f"推理: {h['text']}")
        if h["role"] == "assistant" and h["type"] == "code":
           messages_container.chat_message("assistant").code(f"推理: {h['text']}")

        if h["role"] == "assistant" and h["type"] == "message":
            messages_container.chat_message("assistant").write(h["text"])
    return messages_container

def code_generation(human_input, history):
    # time.sleep(2)
    history.append({"role": "assistant", "text": f"推理: {human_input}", "type": "reasoning"})
    history.append({"role": "assistant", "text": f"dlkfjslkfjlsakfjlsaf", "type": "code"})

    return history

if "history" not in st.session_state:
    st.session_state["history"] = []
if "sql_code" not in st.session_state:
    st.session_state["sql_code"] = []


messages_container = st.container()

if human_input := st.chat_input("请输入你需要咨询的问题 eg., bing 的dau有多少？ "):
    st.session_state["history"].append({"role": "user", "text": human_input})
    
    with messages_container.chat_message("user"):
        st_echarts(options=options)
        with st.expander("Edit chart"):
            url="""https://echarts.apache.org/examples/"""
            st.markdown(f"Paste json and edit chart at here: {url}")
            st.code(json.dumps(options),language="json")

        
    with messages_container.chat_message("user"):
        st.text("**abcd**dfaldskfjlkdsjf\r\ndd法撒旦范德萨发放"+"\n"+"dsfdsaf")
        st.text("""| **Check Item**         | **Link/Status**                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------- |
| **OKR - SA DAU**       | [DAU ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229619)       |
| **OKR - SA Retention** | [Retention ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229646) |
| **OKR - Codex Chat**   | [Codex ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229592)     |

""")
        
