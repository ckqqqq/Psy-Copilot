import streamlit as st
import time
from code_editor import code_editor
from src.Agent import Agent
from src.ToolPGSQL import ToolPGSQL
from src.Formatter import Formatter
from src.AgentExplain import AgentExplain
from src.AgentVisual import AgentVisual
from src.AgentToolUser import AgentToolUser

from CodeEditor import defaut_btn_setting

import json
from code_editor import code_editor
from streamlit_echarts import st_echarts
import random
from datetime import datetime





# Set page configuration
st.set_page_config(
    page_title="Kingfisher",
    page_icon="🐦"
)


# Function to initialize session state

# Vendor webfront text for instruction
st.title("Kingfisher")
st.subheader("Empowering data with large language models.")

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
st.sidebar.code("""$run$ PGSQL""")
st.sidebar.code("""$explain$ Explain the result of the SQL code.""")
st.sidebar.code("""$visualize$ Please draw a line chart of the data.""")
st.sidebar.code("""$usetool$ Please generate a daily check report of  June 6th, 2024.""")
messages_container = st.container()
# def edit_code(origin_code:str):

if "code_editor" in st.session_state and st.session_state["code_editor"]['type']!='':
    print(st.session_state["code_editor"],"Code editor in streamlit is not a shit!!!")


def flash_dialog_history(history,mode="Debug"):
    def flash_code_block(h,is_expand=True):
        pgsql_code=h['text']
        st.write(f"**Code Generation**:")
        # st.code(body=pgsql_code,language="sql",line_numbers=True,visible=is_expand)
        # Remove hint~
        # st.code("try '$run' magic command to run these code",language="markdown")
        if "flash_page_cnt" not in st.session_state:
            st.session_state["flash_page_cnt"]=0
        else:
            st.session_state["flash_page_cnt"]+=1
        with st.expander("Edit Code"):
            @st.cache_resource(hash_funcs={dict: lambda response: response.get("id")})
            def code_editor_listener(code_editor_repsonse):
                if code_editor_repsonse['type'] == "submit" and len(code_editor_repsonse['text']) != 0:
                    st.sidebar.write(code_editor_repsonse)
                    st.session_state['flash_page_cnt']+=1000
                    print("--------------")
                print("###########3",code_editor_repsonse)
            st.write(f"PGSQL_code_editor_{st.session_state['flash_page_cnt']}")
            st.session_state["code_editor"] = code_editor(pgsql_code,lang="pgsql",theme="dark",allow_reset=True,buttons=defaut_btn_setting,key=f"code_editor_{st.session_state['flash_page_cnt']}")
            # warning !!!!! Code editor in streamlit is a totally shit, I strongly recommand that do not try edit code and renew content in code editor, it will cause a lot of problems.
            ## the key of code_editor has conflicts with chat framework. if you are a streamlit master you can write code editing logic here
    for idx, h in enumerate(history):
        if h["role"] == "user":
            messages_container.chat_message("user").write(h["text"])
        elif h["role"] == "assistant" and h["type"] == "reasoning":
            messages_container.chat_message("assistant").write(f"**Reasoning**: {h['text']}")
        elif h["role"] == "assistant" and h["type"] == "code":
            with messages_container.chat_message("assistant"):
                flash_code_block(h,is_expand=False)
        elif h["role"] == "assistant" and h["type"] == "explain":
            with messages_container.chat_message("assistant"):
                st.dataframe(h["dataframe"])
                st.write(h["text"])
        elif h["role"] == "assistant" and h["type"] == "message":
            messages_container.chat_message("assistant").write(h["text"])
        elif h["role"] == "assistant" and h["type"] == "dataframe":
            with messages_container.chat_message("assistant"):
                st.dataframe(h["text"])
        elif h["role"] == "assistant" and h["type"] == "auto":
            if isinstance(h["text"], str):
                with messages_container.chat_message("assistant"):
                    st.text(h["text"])
                if "Daily Check" in h["text"]:
                    
                    st.markdown("""| **Check Item**         | **Link/Status**                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------- |
| **OKR - SA DAU**       | [DAU ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229619)       |
| **OKR - SA Retention** | [Retention ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229646) |
| **OKR - Codex Chat**   | [Codex ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229592)     |

""")
                    # print("string 类型")
            else:
                with messages_container.chat_message("assistant"):
                    st.write(h["text"])
                # Remove hint
                #st.code("try '$visual' or '$explain'",language="markdown")
        elif h["role"] == "assistant" and h["type"] == "chart":
            with messages_container.chat_message("user"):
                st.write("-----------------")
                options_str=h["text"]
                if "echart_flash_page_cnt" not in st.session_state:
                    st.session_state["echart_flash_page_cnt"]=0
                else:
                    st.session_state["echart_flash_page_cnt"]+=1
                try:
                    options=json.loads(options_str)
                    st_echarts(options=options,key=str(st.session_state["echart_flash_page_cnt"]))
                except:
                    st.error("JSON format error")
                # st.markdown("[hhhh](https://img-blog.csdnimg.cn)")

                with st.expander("Edit chart"):
                    url="""https://echarts.apache.org/examples/"""
                    st.markdown(f"Paste json and edit chart at here: {url}")
                    st.code(options_str,language="json")
        else:
            messages_container.chat_message("assistant").write(h["text"])

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
    agent = Agent("dau")
    
    if "target" in st.session_state and st.session_state["target"] is not None:
        target = st.session_state["target"]
        print("--- target ", target)
        agent.change_prompt(target)
    
    agentExplain = AgentExplain() # Agent for explain SQL result
    agentVisual = AgentVisual() # Agent for echart
    toolPGSQL = ToolPGSQL() # Agent for run PGSQL
    formatter = Formatter() # format result decode/encode for GPT input/ouput
    agentToolUser= AgentToolUser()
    print("Agent loaded")
    return {"agent": agent, "toolPGSQL": toolPGSQL, "agentExplain": agentExplain, "formatter": formatter,"agentVisual":agentVisual,"agentToolUser":agentToolUser}

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
if "target" in st.session_state and selected_target!=st.session_state["target"]:
    st.session_state["target"]=selected_target
    st.sidebar.write(f"Analysis target updated to: {selected_target}")
    st.session_state["Agents"]["agent"].change_prompt(st.session_state["target"])
#     st.sidebar.write(st.session_state['target'])

# Function to display dialog history
def string2message(info:str):
    return {"role": "assistant", "text": info, "type": "message"}

# Function to generate code based on user input
def generate_code(human_input, history, mode = "Debug"):
    agent_dict = st.session_state["Agents"]
    agent, formatter = agent_dict["agent"], agent_dict["formatter"]
    max_retries = 2
    retries = 0
    success = False
    # Generate code and retry 2 times if failed
    while retries < max_retries and not success:
        str_query = agent.chat(human_input)
        json_query = formatter.json_decode(
            str_query,
            need_key_list=["Analysis","SQL", "input", "reasoning"]
        )
        
        retries += 1    

        if json_query is None:
            history.append(string2message( "Error decoding JSON: 0_0 " + str_query))
            continue

        print("========")
        print(json_query["Analysis"]["SQL"])
        print("========")
        sql_result = formatter.correct_sql_format(str(json_query["Analysis"]["SQL"]))

        if sql_result != "wrong":
            success = True
        else:
            # correct the sql format
            json_query["Analysis"]["SQL"]=sql_result
    
    if json_query is None:
        history.append(string2message( "Error decoding JSON: 0_0 " + str_query))
    else:
        history.append({"role": "assistant", "text": json_query["Analysis"]["reasoning"], "type": "reasoning"})
        history.append({"role": "assistant", "text": json_query["Analysis"]["SQL"], "type": "code"})
        st.session_state["gen_json"] = json_query

    return history

# Function to run SQL code
def run_code(human_instruction,history):
    agent_dict = st.session_state["Agents"]
    toolPGSQL = agent_dict["toolPGSQL"]
    formatter = agent_dict["formatter"]
    gen_json = st.session_state["gen_json"]
    print(gen_json)
    if len(gen_json) == 0:
        gen_json["Analysis"]["SQL"]
        history.append({"role": "assistant", "text": "Empty code generation or decoding error", "type": "message"})
    else:
        sql_query = gen_json["Analysis"]["SQL"]
        print("Running PGSQL")
        sql_res_df = toolPGSQL.execute_v2(sql_query)
        print("PGSQL run completed")
        if sql_res_df.empty:
            history.append({"role": "assistant", "text": "PGSQL query returned no results", "type": "message"})
            return history
        
        st.session_state["gen_json"]["Analysis"].update({"sql_res_df": sql_res_df})
        history.append({"role": "assistant", "text": formatter.df_application_id_2_name(sql_res_df), "type": "dataframe"})
    return history

# Function to explain SQL code results
def explain_code(human_instruction,history):
    agent_dict = st.session_state["Agents"]
    agentExplain = agent_dict["agentExplain"]
    formatter = agent_dict["formatter"]
    if "gen_json" not in st.session_state or len(st.session_state["gen_json"])==0:
        history.append(string2message("Code Not Found! Please ask question first."))
    else:
        gen_json = st.session_state["gen_json"]
        human_input =gen_json["Analysis"]["input"]+gen_json["Analysis"]["reasoning"]
        sql_res_df = gen_json["Analysis"]["sql_res_df"]
        print("Explaining")
        if human_instruction!="":
            query=human_input+"\Instrution: "+human_instruction
        else:
            query=human_input
        explain_raw_str = agentExplain.explain(query=query, df_csv_format=sql_res_df.to_csv(index=False))
        explain_json=formatter.json_decode(explain_raw_str,need_key_list=["explain"])
        if None==explain_json:
            explain_markdown=explain_raw_str
        else:
            explain_markdown=explain_json["explain"]
        history.append({"role": "assistant", "text": explain_markdown,"dataframe":sql_res_df, "type": "explain"})
    return history

def visualize(human_instruction,history):
    agent_dict = st.session_state["Agents"]
    agentVisual = agent_dict["agentVisual"]
    formatter = agent_dict["formatter"]
    if "gen_json" not in st.session_state or len(st.session_state["gen_json"])==0:
        history.append(string2message("Code Not Found! Please ask question for running code first."))
        print("gen_json not in st.session_state or len(st.session_state[gen_json])==0:")
    else:
        gen_json = st.session_state["gen_json"]
        human_input = gen_json["Analysis"]["input"]
        sql_res_df = gen_json["Analysis"]["sql_res_df"]
        print("Explaining",sql_res_df.to_csv(index=False))
        chart_json_str = agentVisual.visual(human_instruction=human_instruction,df_csv_format=sql_res_df.to_csv(index=False))
        history.append({"role": "assistant", "text": chart_json_str, "type": "chart"})
    return history

def use_tool(human_instruction,history):
    agent_dict = st.session_state["Agents"]
    agentToolUser = agent_dict["agentToolUser"]
    tool_result = agentToolUser.use_tool(query=human_instruction)
    history.append({"role": "assistant", "text": tool_result, "type": "auto"})
    return history

# Chat input for user interaction
if human_input := st.chat_input("Enter your question or specific command (e.g., bing's dau count?): "):
    st.session_state["history"].append({"role": "user", "text": human_input})
    
    if mode == "Prod":
        
        with st.spinner("""AI is processing your request, generating answers, querying databases, and explaining results... \n
                        ❤ Thank you for your patience. """):
            st.session_state["history"] = generate_code(human_input, history=st.session_state["history"])
            st.session_state["history"] = run_code(human_input, history=st.session_state["history"])
            st.session_state["history"] = explain_code(human_input, history=st.session_state["history"])
            st.session_state["history"] = visualize(human_input,history=st.session_state["history"])
            flash_dialog_history(history=st.session_state["history"],mode="Prod")
    else:
        if "$" in human_input:
            
            if human_input.count("$") > 1:
                # human_input eg $run
                human_instruction=human_input.split("$")[-1]
            else:
                # eg show me a bar chart
                human_instruction=""
            # distinguish magic commands
            if "run" in human_input or "RUN" in human_input:
                with st.spinner("AI is running code to query databases.  Thank you for your patience.... (ง •_•)ง"):
                    st.session_state["history"] = run_code(human_instruction=human_instruction,history=st.session_state["history"])
                    flash_dialog_history(history=st.session_state["history"])
            elif "explain" in human_input or "EXPLAIN" in human_input:
                with st.spinner("AI is analysis the data.  Thank you for your patience.... (￣︶￣)↗"):
                    st.session_state["history"] = explain_code(human_instruction=human_instruction,history=st.session_state["history"])
                    flash_dialog_history(history=st.session_state["history"])
            elif "visualize" in human_input or "VISUALIZE" in human_input or "visual" in human_input:
                with st.spinner("AI is generating chart. Thank you for your patience....╰(*°▽°*)╯"):
                    st.session_state["history"] = visualize(human_instruction=human_instruction,history=st.session_state["history"])
                    flash_dialog_history(history=st.session_state["history"])
            elif "tooluse" in human_input or "TOOLUSE" in human_input or "usetool" in human_input or "USETOOL" in human_input:
                with st.spinner("AI is calling functions. Thank you for your patience....╰(*°▽°*)╯"):
                    st.session_state["history"] = use_tool(human_instruction=human_instruction,history=st.session_state["history"])
                    flash_dialog_history(history=st.session_state["history"])
            else:
                st.session_state["history"].append(string2message("Command not recognized. (T°▽°T)"))
                flash_dialog_history(history=st.session_state["history"])
        else:
            with st.spinner("AI is generating PGSQL code, Thank you for your patience....(＋▽＋)"):
                st.session_state["history"] = generate_code(human_input, history=st.session_state["history"])
                flash_dialog_history(history=st.session_state["history"])