import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
# from src.graph.graph_builder_from_json import GraphBuilder
from src.graph.graph_rag import GraphRAG
from src.graph.graph_viewer import visualize_neo4j_subgraph

import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import json
import uuid
env_path="/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

st.set_page_config(page_title="Demo", layout="wide",initial_sidebar_state="collapsed")
# 改了这里
st.title("Demo")
# 插入 html实验 https://blog.csdn.net/m0_74061452/article/details/139910706

def draw_graph_by_wiki(search_item:str):
    # print(type(progress_bar),status_text)
    # build_graph_llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    # graph_builder = GraphBuilder(build_graph_llm)
    # status_text.text("SFBT")
    pass
    
def reset_graph():
    """ reset graph 重置图"""
    # build_graph_llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    # graph_builder = GraphBuilder(llm=build_graph_llm)
    # graph_builder.reset_graph()
    # 直接对数据库进行处理，删除对应的图
    pass
    
def get_response(user_query: str,chat_history) -> str:
    """
    For the given question will formulate a search query and use a custom GraphRAG retriever 
    to fetch related content from the knowledge graph.
    提问和反馈回答
    """
    print("Chathistory")
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USERNAME"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "AI4AI666"
    
    llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    rag_llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    # rag= 
    rag = GraphRAG(llm=rag_llm)
    # 提示模板，其中context是检索结果
    # template = """Answer the question based only on the following context:
    # {context}
    # Here is 
    # Question: {question}
    # Use natural language.
    # Answer:"""
    prompt = ChatPromptTemplate.from_template("""You are a mental health supporter and not an AI. You should use your knowledge of Solution-Focused Brief Therapy to provide short and natural psychological responses. Your dialogs are focused on solutions, aiming to shift the focus from problems to resolutions. You are dedicated to guiding users to take small steps in discovering their strengths and qualities amidst difficulties. There are some example and guide: {retrieved_text} There is chat history: {chat_history}  Question: {user_query}  Please generate Answer:""")

    # 测试代码
    # question,embedding_model=OpenAIEmbeddings(),exclude_relations=["MENTIONS"]
    embedding_model=OpenAIEmbeddings()
    # 并行进行不同维度的处理
    retrieved_chain=(
        ## RunnableParallel 这是一个并行处理模块，它接受一个字典作为参数，字典的键是处理步骤的名称，值是处理函数或模块。
        RunnableParallel(
            {
            
            "retrieved_result1": lambda x: rag.unstructured_retriever(user_query,embedding_model=embedding_model,exclude_relations=["MENTIONS"])
            }
        )
    )
    rag_dict=retrieved_chain.invoke({"user_query": user_query})
    
    unstructured_text=rag_dict["retrieved_result1"]["result"]
    node_ids=rag_dict["retrieved_result1"]["node_ids"]
    print(node_ids)
    # 增加检索到的节点
    st.session_state.graph_node_ids.extend(node_ids)
    st.session_state.showed_node_id=node_ids[0]
    retrieved_text=unstructured_text
    
    chain = (
        # RunnablePassthrough()。这表示 "question" 处理步骤不会对输入数据进行任何修改，而是直接将输入数据传递到下一个处理步骤。
        prompt
        | llm
        | StrOutputParser()
    )
    # Using invoke method to get response
    response=chain.invoke({"retrieved_text":retrieved_text,"chat_history": chat_history, "user_query": user_query})
    # response="aaaa"
    return response



if "graph_node_ids" not in st.session_state:
    st.session_state.graph_node_ids=[]
if "showed_node_id" not in st.session_state:
    st.session_state.showed_node_id="id: document0summary000070"


                
# if __name__=="__main__":
col_left, col_right = st.columns(2)
# 侧边栏
with st.sidebar:
    st.header("Graph Management")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Draw Graph"):
            progress_bar = st.progress(0)
            draw_graph_by_wiki("Psychotherapy")
    with col2:
        if st.button("Reset Graph"):
            reset_graph()
# 左边的图
with col_left:
    messages_container = st.container(height=800)
    # with messages_container:
    def render_message(message):
        """渲染函数,注意一定要在container后面定义"""
        if isinstance(message, HumanMessage):
            with messages_container.chat_message("Human"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with messages_container.chat_message("AI"):
                st.write(message.content)
    def render_last_message():
        render_message(st.session_state.chat_history[-1])
    def render_all_message():
        for message in st.session_state.chat_history:
            render_message(message)
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
                    AIMessage(content="Hello, I'm here to help. Ask me anything!")
                ]
        render_all_message()
    else:
        render_all_message()
    # 全局变量，一个消息容纳器

    if user_query := st.chat_input("Ask a question....", key='user_query_2'):
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        render_last_message()
        rag_response = get_response(user_query=user_query, chat_history=st.session_state.chat_history)
        st.session_state.chat_history.append(AIMessage(content=rag_response))
        render_last_message()


            
#右边边的图            
with col_right:
    if st.session_state.showed_node_id:
        node_id = st.session_state.showed_node_id
        neighbor_type = "ALL" 
        fig = visualize_neo4j_subgraph(node_identity=node_id, constraint_node_properties=neighbor_type,depth=2)
        st.plotly_chart(fig,use_container_width=True)
