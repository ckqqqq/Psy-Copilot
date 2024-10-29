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

# st.set_page_config(page_title="Demo", layout="wide",initial_sidebar_state="collapsed")
# 改了这里\
    
def test(user_query:str):
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
    llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    prompt = ChatPromptTemplate.from_template("""You are a mental health supporter and not an AI. You should use your knowledge of Solution-Focused Brief Therapy to provide short and natural psychological responses. Your dialogs are focused on solutions, aiming to shift the focus from problems to resolutions. You are dedicated to guiding users to take small steps in discovering their strengths and qualities amidst difficulties. There are some example and guide: {retrieved_text} There is chat history: {chat_history}  Question: {user_query}  Please generate Answer:""")

    # 测试代码
    # question,embedding_model=OpenAIEmbeddings(),exclude_relations=["MENTIONS"]
    embedding_model=OpenAIEmbeddings()
    # 并行进行不同维度的处理
    retrieved_chain=(
        ## RunnableParallel 这是一个并行处理模块，它接受一个字典作为参数，字典的键是处理步骤的名称，值是处理函数或模块。
        RunnableParallel(
            {
            
            "retrieved_result": lambda x: rag.unstructured_retriever_type2(user_query,embedding_model=embedding_model,exclude_relations=["MENTIONS"])
            }
        )
    )
    rag_dict=retrieved_chain.invoke({"user_query": user_query})
    
    unstructured_text=rag_dict["retrieved_result"]["result"]
    print(unstructured_text)
    # structured_text=rag.structured_retriever("Therapist can use CBT",result_num_limit=5,exclude_relations=["MENTIONS"])
    print("检索结果外部输出")
    # print(structured_text)
    
test("我的养母打了我一巴掌")