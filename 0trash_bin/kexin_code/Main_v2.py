import streamlit as st
import time
import json
from code_editor import code_editor
from Agent import Agent
from ToolPGSQL import ToolPGSQL
from Formatter import Formatter
from AgentExplain import AgentExplain

# Set page configuration
st.set_page_config(
    page_title="DataCopilot",
    page_icon=":robot:"
)

# Function to initialize session state
@st.cache_resource
def initialize_st():
    print("Initializing page, loading Agent...")
    target = "auto"
    agent = Agent("dau")
    
    if "target" in st.session_state:
        target = st.session_state["target"]
        print("target", target)
        agent.change_prompt(target)
    
    agentExplain = AgentExplain()
    toolPGSQL = ToolPGSQL()
    formatter = Formatter()
    print("Agent loaded")
    
    return {"agent": agent, "toolPGSQL": toolPGSQL, "agentExplain": agentExplain, "formatter": formatter}

# Load Agents with a spinner
with st.spinner("Loading Agents, please wait..."):
    st.session_state["Agents"] = initialize_st()

# Main title and subtitle
st.title("Data-Jarvis")
st.subheader("Empowering data with large language models.")


# Sidebar with parameters
mode = st.sidebar.radio('Select Mode', ['Debug', 'Prod'])

# Sidebar with parameters
max_length = st.sidebar.slider('max_length', 0, 4096, 2048, step=1,help="The maximum length of tokens.")
top_p = st.sidebar.slider('top_p', 0.0, 1.0, 0.6, step=0.01)
temperature = st.sidebar.slider('temperature', 0.0, 1.0, 0.95, step=0.01)
sql_timeout = st.sidebar.slider('SQL_timeout', 0, 100, 10, step=1)

# Initialize session state variables if they don't exist
if "target" not in st.session_state:
    st.session_state["target"] = None
if "history" not in st.session_state:
    st.session_state["history"] = []
if "gen_json" not in st.session_state:
    st.session_state["gen_json"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []

# Radio button to select target
selected_target = st.sidebar.radio(
    "Select target",
    ["dau", "miniapp", "auto"],
    captions=["E.g., Bing APP DAU in the last 10 days.", "What is the highest DAU Miniapp in Bing APP?", "Not tested."]
)

st.sidebar.subheader("Specific commands include: 'run' code, 'explain' result")
# Function to change prompt based on selection
def change_prompt(target):
    st.sidebar.write(f"Target updated to: {target}")
    st.session_state["target"] = target
    st.session_state["Agents"]["agent"].change_prompt(target)

# Agent for parameters
# Function to update agent parameters
def update_agent_parameters():
    agent = st.session_state["Agents"]["agent"]
    agent.update_params(temperature=temperature, max_tokens=max_length, top_p=top_p)


# Check for new selection and call function
if selected_target != st.session_state["target"]:
    change_prompt(selected_target)

# Update agent parameters whenever sliders change
update_agent_parameters()

# Check for new selection and call function
if selected_target != st.session_state["target"]:
    st.session_state["target"] = selected_target
    change_prompt(selected_target)

# Function to display dialog history
def flash_dialog_history(history):
    for idx, h in enumerate(history):
        if h["role"] == "user":
            messages_container.chat_message("user").write(h["text"])
        if h["role"] == "assistant" and h["type"] == "reasoning":
            messages_container.chat_message("assistant").write(f"Reasoning: {h['text']}")
        if h["role"] == "assistant" and h["type"] == "code":
            messages_container.chat_message("assistant").write(f"Code Generation:")
            messages_container.chat_message("assistant").code(h['text'])
        if h["role"] == "assistant" and h["type"] == "message":
            messages_container.chat_message("assistant").write(h["text"])
        if h["role"] == "assistant" and h["type"] == "dataframe":
            messages_container.chat_message("assistant").dataframe(h["text"])
    return messages_container

# Function to generate code based on user input
def generate_code(human_input, history, mode = "Debug"):
    agent_dict = st.session_state["Agents"]
    agent, formatter = agent_dict["agent"], agent_dict["formatter"]
    str_query = agent.chat(human_input)
    print("----------")
    print(str_query)
    
    with open("debug.txt", "w", encoding="utf-8") as f:
        f.write(f"Query: {str_query}")
    
    json_query = formatter.json_decode(
        str_query,
        need_key_list=["Analysis","SQL", "input", "reasoning"]
    )
    print("========")
    print(json_query)
    sql_history_list = []
    if json_query is None:
        sql_history_list.append({"role": "assistant", "text": "Error decoding JSON: " + str_query, "type": "message"})
    else:
        sql_history_list.append({"role": "assistant", "text": json_query["Analysis"]["reasoning"], "type": "reasoning"})
        sql_history_list.append({"role": "assistant", "text": json_query["Analysis"]["SQL"], "type": "code"})
        st.session_state["gen_json"] = json_query

    if (mode == "Debug"):
        history = history + sql_history_list

    return history

# Function to run SQL code
def run_code(human_input, history):
    agent_dict = st.session_state["Agents"]
    toolPGSQL = agent_dict["toolPGSQL"]
    formatter = agent_dict["formatter"]
    gen_json = st.session_state["gen_json"]
    if len(gen_json) == 0:
        gen_json["Analysis"]["SQL"]
        history.append({"role": "assistant", "text": "Empty code generation or decoding error", "type": "message"})
    else:
        sql_query = gen_json["Analysis"]["SQL"]
        print("Running PGSQL")
        sql_res_df = toolPGSQL.execute_query_with_pandas(sql_query)
        print("PGSQL run completed")
        st.session_state["gen_json"]["Analysis"].update({"sql_res_df": sql_res_df})
        history.append({"role": "assistant", "text": formatter.df_application_id_2_name(sql_res_df), "type": "dataframe"})
    return history

# Function to explain SQL code results
def explain_code(human_input, history):
    agent_dict = st.session_state["Agents"]
    agentExplain = agent_dict["agentExplain"]
    formatter = agent_dict["formatter"]
    gen_json = st.session_state["gen_json"]
    if len(gen_json) == 0:
        gen_json["Analysis"]["SQL"]
        history.append({"role": "assistant", "text": "Code not executed", "type": "message"})
    else:
        human_input = gen_json["Analysis"]["input"]
        sql_res_df = gen_json["Analysis"]["sql_res_df"]
        print("Explaining")
        AI_explain = agentExplain.explain(query=human_input, df_csv_format=sql_res_df.to_csv(index=False))
        history.append({"role": "assistant", "text": "PGSQL query results indicate:\n" + formatter.app_id_2_name(AI_explain), "type": "message"})
    return history

messages_container = st.container()

# Chat input for user interaction
if human_input := st.chat_input("Enter your question or specific command (e.g., bing's dau count?): "):
    st.session_state["history"].append({"role": "user", "text": human_input})
    
    if mode == "Prod":
        
        with st.spinner("""AI is processing your request, generating answers, querying databases, and explaining results... \n
                        ❤ Thank you for your patience. """):
            st.session_state["history"] = generate_code(human_input, history=st.session_state["history"], mode="Prod")
            st.session_state["history"] = run_code(human_input, history=st.session_state["history"])
            st.session_state["history"] = explain_code(human_input, history=st.session_state["history"])
            flash_dialog_history(history=st.session_state["history"])
    else:
        if human_input == "run":
            with st.spinner("Executing code, please wait..."):
                st.session_state["history"] = run_code(human_input, history=st.session_state["history"])
                flash_dialog_history(history=st.session_state["history"])
        
        elif human_input == "explain":
            with st.spinner("Explaining, please wait..."):
                st.session_state["history"] = explain_code(human_input, history=st.session_state["history"])
                flash_dialog_history(history=st.session_state["history"])
        
        else:
            with st.spinner("Thinking, please wait..."):
                st.session_state["history"] = generate_code(human_input, history=st.session_state["history"], mode="Debug")
                flash_dialog_history(history=st.session_state["history"])