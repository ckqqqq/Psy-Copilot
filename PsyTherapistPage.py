import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from src.graph.graph_rag import GraphRAG
from src.graph.graph_viewer import visualize_neo4j_subgraph
from src.statistics.topic import show_topic_chart
from src.pages.markdown import download_markdown
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import json
import uuid
import plotly.express as px
from streamlit_plotly_events import plotly_events  # Import the plotly events component

# Load environment variables
env_path = "/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

# Set Streamlit page configuration
st.set_page_config(page_title="Demo", layout="wide", initial_sidebar_state="collapsed")

# Initialize session state variables if they don't exist
if "graph_node_ids" not in st.session_state:
    st.session_state.graph_node_ids = ["document0summary000070"]
if "showed_node_id" not in st.session_state:
    st.session_state.showed_idx = 0
if "current_graph_index" not in st.session_state:
    st.session_state.current_graph_index = 0
if "graphs" not in st.session_state:
    st.session_state.graphs = ["Psychotherapy", "Cognitive Behavioral Therapy", "Solution-Focused Brief Therapy"]  # Example graph names
if "modal_content" not in st.session_state:
    st.session_state.modal_content = ""
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

# Sidebar: Language Model Configuration Sliders
with st.sidebar:
    st.header("Language Model Settings")
    # Slider for Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
        help="Controls the randomness of the model's output. Lower values make the output more deterministic."
    )
    # Slider for Top-p
    top_p = st.slider(
        "Top-p",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.01,
        help="Controls the diversity of the model's output. Lower values make the output more focused."
    )
    # Slider for Max Tokens
    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=2000,
        value=500,
        step=50,
        help="The maximum number of tokens to generate in the response."
    )
    
    st.markdown("---")  # Separator
    image_path = './QR.jpg'

        # 使用st.image函数展示图片
    st.image(image_path, use_column_width=True)
    
    link_text = "Try Our Demo"
    url = "https://anonymous.4open.science/r/Psy-Copilot-6EA1" 

    # 使用st.markdown函数创建超链接
    st.markdown(f'<a href="{url}" target="_blank">{link_text}</a>', unsafe_allow_html=True)
    st.header("Graph Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Draw Graph"):
            progress_bar = st.progress(0)
            # draw_graph_by_wiki(st.session_state.graphs[st.session_state.current_graph_index])
            progress_bar.progress(100)
    with col2:
        if st.button("Reset Graph"):
            reset_graph()
    model_index = st.sidebar.radio("Retrieve Method Selection", [ "unstructured retrieve by COT-index", "unstructured retrieve by dialogue-index","structured retrieve - test"])

# Function to draw graph based on a search item
# def draw_graph_by_wiki(search_item: str):
#     """
#     Placeholder function to draw graph based on a search item.
#     Implement the actual logic as per your backend.
#     """
#     # Example: Reset showed_node_id or any other logic
#     st.session_state.showed_idx = "document0summary000070"
#     st.session_state.graphs = ["Psychotherapy", "Cognitive Behavioral Therapy", "Solution-Focused Brief Therapy"]

# Function to reset the graph
def reset_graph():
    """
    Placeholder function to reset the graph.
    Implement the actual logic to clear the graph from the database or reset session state.
    """
    pass
    # st.session_state.graph_node_ids = ["document0summary000070"]
    # st.session_state.showed_idx = 

# Function to get AI response based on user query and chat history
def get_response(user_query: str, chat_history) -> str:
    """
    For the given question, formulate a search query and use a custom GraphRAG retriever 
    to fetch related content from the knowledge graph.
    """
    print("Chat history received for processing.")
    
    # Set Neo4j connection details from environment variables
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USERNAME"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "AI4AI666"
    
    # Initialize language models with user-configured parameters
    llm = ChatOpenAI(
        model=os.environ["DEEPSEEK_API_MODEL"],
        temperature=temperature,  # Use temperature from sidebar
        top_p=top_p,              # Use top_p from sidebar
        max_tokens=max_tokens,    # Use max_tokens from sidebar
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_API_BASE"]
    )
    rag_llm = ChatOpenAI(
        model=os.environ["DEEPSEEK_API_MODEL"],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_API_BASE"]
    )
    
    rag = GraphRAG(llm=rag_llm)
    
    # Define the prompt template with placeholders for retrieved text and chat history
    prompt = ChatPromptTemplate.from_template(
        """You are a mental health supporter and not an AI. You should use your knowledge of Solution-Focused Brief Therapy to provide short and natural psychological responses. Your task is to respond naturally and coherently to what the user is currently saying, based on the history of your conversation with the user. What you say should not be too long.
        
        Here are some ideas and examples you can use when responding to your users:
        {retrieved_text}
        
        Below is the history of the conversations you've had with your users: 
        {chat_history}
        
        Now the user says:
        {user_query}
        
        Please respond to what the user said based on the history of the conversation between you and the user:
        """
    )
    
    # Initialize embeddings model
    embedding_model = OpenAIEmbeddings()
    
    # Concatenate chat history into a single string with proper labels
    new_user_query = ''
    if len(chat_history) > 7:
        chat_history = chat_history[-7:]  # Limit to last 7 messages
    for message in chat_history:
        if isinstance(message, AIMessage):
            new_user_query += "Supporter " + message.content + "\n"
        elif isinstance(message, HumanMessage):
            new_user_query += "Seeker " + message.content + "\n"
    
    # Parallel retrieval of related content from the knowledge graph
    retrieved_chain = RunnableParallel(
        {
            "retrieved_result": lambda x: rag.unstructured_retriever_type2(
                new_user_query,
                embedding_model=embedding_model,
                exclude_relations=["MENTIONS"],
                num_limit=2
            )
        }
    )
    rag_dict = retrieved_chain.invoke({"user_query": user_query})
    
    # Extract retrieved text and node IDs
    unstructured_text = rag_dict["retrieved_result"]["result"]
    node_ids = rag_dict["retrieved_result"]["node_ids"]
    
    # print("Retrieved Result:", rag_dict["retrieved_result"])
    print("* Node IDs:"*10, node_ids)
    
    # Update session state with retrieved node IDs
    if node_ids and len(node_ids) > 0:
        st.session_state.showed_idx=len(st.session_state.graph_node_ids)
        st.session_state.graph_node_ids.extend(node_ids)
        
   
    
    retrieved_text = unstructured_text
    print("Unstructured retrieved text:", retrieved_text)
    
    # Define the chain of processing steps: prompt -> LLM -> parse output
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    # Invoke the chain to get the AI response
    response = chain.invoke({
        "retrieved_text": retrieved_text,
        "chat_history": chat_history,
        "user_query": user_query
    })
    
    return response

# Function to update the currently displayed node ID and refresh the graph


# Function to render messages in the chat
def render_message(message):
    if isinstance(message, HumanMessage):
        with messages_container.chat_message("Human"):
            st.write(f"{message.content} ")  # Adding emoji for human messages
    elif isinstance(message, AIMessage):
        with messages_container.chat_message("AI"):
            st.write(f"{message.content} 🤖")  # Adding emoji for AI messages

# Main layout with two columns: Left for chat, Right for knowledge graph
col_left, col_right = st.columns(2)

with col_left:
    a,b=st.columns(2)
    st.title("Psy-Copilot")

    messages_container = st.container(height=720)
    
    # Function to render the last message in the chat
    def render_last_message():
        render_message(st.session_state.chat_history[-1])
    
    # Function to render all messages in the chat
    def render_all_message():
        for message in st.session_state.chat_history:
            render_message(message)
    
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello 👋, I'm here to help. Ask me anything!")
        ]
        render_all_message()
    else:
        render_all_message()
    
    # Chat input box with enhanced features
    if user_query := st.chat_input("Ask a question.... 😊", key='user_query_2'):
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        render_last_message()
        previous_showed_node_id = st.session_state.graph_node_ids[st.session_state.showed_idx]
        # Display a spinner while retrieving the response
        with st.spinner("Retrieve for Psy-COT... 🕒"):
            rag_response = get_response(user_query=user_query, chat_history=st.session_state.chat_history)
            
         # 检查 showed_node_id 是否未发生变化
        if st.session_state.graph_node_ids[st.session_state.showed_idx] == previous_showed_node_id:
            # 递增 showed_node_id，但不超过 graph_node_ids 的长度
            st.session_state.showed_idx = min(
                st.session_state.showed_idx + 1,
                len(st.session_state.graph_node_ids) - 1
            )
        
        st.session_state.chat_history.append(AIMessage(content=rag_response))
        render_last_message()
    # import streamlit as st


with col_right:
    st.title("Sub-graph of Psy-COT")
    empty_place_holder = st.empty()
    # Function to render the right column (knowledge graph and pie chart)
    def render_right_col():
        node_identity=st.session_state.graph_node_ids[st.session_state.showed_idx]
        print("渲染"*10,node_identity)
        fig = visualize_neo4j_subgraph(
            node_identity=node_identity,
            constraint_node_properties="ALL",
            depth=2
        )
                # 定义内圈labels和所有颜色
        
        # Use plotly_events to capture click events
        # clicked_points = plotly_events(fig, click_event=True, hover_event=False, select_event=False)
        
        # If a node is clicked, update session state to show modal
        # if clicked_points:
        #     clicked_point = clicked_points[0]
        #     # Assuming customdata is a dict with 'node_id', 'label', 'type', 'text'
        #     node_info = clicked_point.get('customdata', {})
        #     st.session_state.modal_content = f"**Node ID:** {node_info.get('node_id', 'N/A')}\n\n**Label:** {node_info.get('label', 'N/A')}\n\n**Type:** {node_info.get('type', 'N/A')}\n\n**Text:** {node_info.get('text', 'N/A')}"
        #     st.session_state.show_modal = True
        
        # Display the graph using Plotly
        st.plotly_chart(fig, use_container_width=True, key=node_identity)
    # Initial render of the right column
    # if st.session_state.showed_idx:
    render_right_col()
    
        # Add an expander for the download button
    with st.expander("Download Diagnosis Report"):

        
        if st.button("Download AI-gen Diagnosis Report"):
            markdown_content = download_markdown(file_name=st.session_state.graph_node_ids[st.session_state.showed_idx])
            st.download_button(
                label="Download Markdown File",
                data=markdown_content,
                file_name=st.session_state.graph_node_ids[st.session_state.showed_idx]+".md",
                mime="text/markdown"
            )

        
                # empty_place_holder.write(st.session_state.showed_idx[-6:])
            # neighbor_type = "ALL" 
            # fig = visualize_neo4j_subgraph(node_identity=st.session_state.showed_idx, constraint_node_properties=neighbor_type,depth=2)
            # st.plotly_chart(fig, use_container_width=True,key=st.session_state.showed_idx)
        
    
    # Function to render the right column with graph switching
    # def render_right_col_with_switch():
    #     # Display the current graph based on the current_graph_index
    #     current_graph = st.session_state.graphs[st.session_state.current_graph_index]
    #     st.session_state.showed_idx = "document0summary000070"  # Reset to default node
        
    #     fig = visualize_neo4j_subgraph(
    #         node_identity=st.session_state.showed_idx,
    #         constraint_node_properties="ALL",
    #         depth=2
    #     )
        
    #     # Display the graph
    #     st.plotly_chart(fig, use_container_width=True, key=current_graph)
        
        # # Pie chart below the graph
        # pie_data = {
        #     'Category': ['A', 'B', 'C'],
        #     'Values': [30, 50, 20]
        # }
        # pie_df = px.data.frame(pie_data)
        # pie_fig = px.pie(pie_df, names='Category', values='Values', title='Sample Pie Chart')
        # st.plotly_chart(pie_fig, use_container_width=True)
    # def update_showed_node_id(node_id: str):
    #     st.session_state.showed_idx = node_id
    #     print("当前子图的核心id",st.session_state.showed_idx)
    #     render_right_col()
    # Buttons to switch between graphs
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("< Previous"):
            if st.session_state.current_graph_index > 0:
                st.session_state.current_graph_index -= 1
                render_right_col()
    with col_next:
        if st.button("Next >"):
            if st.session_state.current_graph_index < len(st.session_state.graphs) - 1:
                st.session_state.current_graph_index += 1
                render_right_col()
    


# 创建 Streamlit 应用
    def show_statistics():
        fig=show_topic_chart()
        st.plotly_chart(fig)
    show_statistics()
        

# Modal Simulation for Node Clicks
modal_placeholder = st.empty()

if st.session_state.show_modal:
    with modal_placeholder.container():
        st.markdown("### Node Details")
        st.markdown(st.session_state.modal_content)
        if st.button("Close"):
            st.session_state.show_modal = False
