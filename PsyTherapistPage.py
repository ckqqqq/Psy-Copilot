import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from src.graph.graph_builder import GraphBuilder
from src.graph.graph_rag import GraphRAG
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
env_path="/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

st.set_page_config(page_title="Demo", layout="wide")
st.title("Demo")
#

def draw_graph_by_wiki(search_item:str):
    # print(type(progress_bar),status_text)
    build_graph_llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    graph_builder = GraphBuilder(build_graph_llm)
    graph_builder.extract_wikipedia_content(search_item)
    print("graph constructed")
    # status_text.text("SFBT")
    
def reset_graph():
    """ reset graph 重置图"""
    build_graph_llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    graph_builder = GraphBuilder(llm=build_graph_llm)
    graph_builder.reset_graph()
    # 直接对数据库进行处理，删除对应的图
    
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
    rag = GraphRAG(llm=rag_llm)
    search_query = rag.create_search_query(chat_history, user_query)
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    Use natural language and be concise.
    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)
    print("***************\n","rag retriever",rag.retriever(search_query))
    print("***************\n","rag retriever")
    # 使用langchain的chain进行处理，分别传入检索器，提示和，大语言模型和输出
    chain = (
        # RunnableParallel 这是一个并行处理模块，它接受一个字典作为参数，字典的键是处理步骤的名称，值是处理函数或模块。在这个例子中，有两个处理步骤："context"和"question"
        RunnableParallel(
            {
                "context": lambda x: rag.retriever(search_query),
                "question": RunnablePassthrough(),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    # Using invoke method to get response
    response=chain.invoke({"chat_history": chat_history, "question": user_query})
    # response="NB"
    return response

def get_not_rag_response(user_query: str,chat_history:list) -> str:
    """
    generation without RAG
    """
    llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    prompt = ChatPromptTemplate.from_template("You are a helpful assistant. There is chat history: {chat_history}  Question: {user_query}  Please generate Answer:")
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    response=chain.invoke({"chat_history": chat_history, "user_query": user_query})
    return response

# print(get_response("what is Garmin_Forerunner? Please give all reference data"))
# Initialise session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I'm here to help. Ask me anything!")
    ]
if __name__=="__main__":
    
    user_query = st.chat_input("Ask a question....")
    if user_query is not None and user_query != "":
        # 人类回复显示
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        rag_response = get_response(user_query=user_query,chat_history= st.session_state.chat_history)
        # Rag response显示
        st.session_state.chat_history.append(AIMessage(content=rag_response))

    # Print the chat history
    for message in st.session_state.chat_history:
        # 如果chat_history的内容有变化则会自动运行此命令
        if isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)

    with st.sidebar:
        st.header("Graph Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Draw Graph"):
                progress_bar = st.progress(0)# 进度条
                # status_text = st.empty()
                draw_graph_by_wiki("Psychotherapy")
        with col2:
            if st.button("Reset Graph"):
                reset_graph()

#  测试模块
# if __name__=="__main__":
    
#     # print("Test")
#     print(get_response("what is SFBT? I want to kwnow case study",[
#         AIMessage(content="Hello, I'm here to help. Ask me anything!")
#     ]))

    # draw_graph_by_wiki(search_item="SFBT")