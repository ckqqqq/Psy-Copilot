"""
Script responsible for build a knowledge graph using
Neo4j from unstructured text
"""
# 
import os
from typing import List
from langchain.text_splitter import TokenTextSplitter
from langchain_community.document_loaders import WikipediaLoader, YoutubeLoader, TextLoader
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI


from langchain_community.graphs.graph_document import GraphDocument,Node,Relationship
from langchain_community.graphs import Neo4jGraph

from dotenv import load_dotenv
env_path="/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)
print(os.environ["DEEPSEEK_API_BASE"],os.environ["DEEPSEEK_API_MODEL"])
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "AI4AI666"
""
class GraphBuilder():
    """
    Encapsulates the core functionality requires to build a full knowledge graph 
    from multiple sources of unstructured text

    _extended_summary_
    这是 neo4j 图数据库的构建器，我们使用其作为图的构造脚手架，在 http://10.110.147.66:7474/browser/ 中直接就能访问其图的内容!
    """
    def __init__(self,llm):
        self.graph = Neo4jGraph(username="neo4j",password="AI4AI666")
        self.llm = llm

    def chunk_document_text(self, raw_docs):
        """
        先将文档划分为定长的 str 再将其做进一步的分类
        Accepts raw text context extracted from source and applies a chunking 
        algorithm to it. 

        Args:
            raw_docs (str): The raw content extracted from the source

        Returns:
            List: List of document chunks
        """
        print("Text spliting")
        text_splitter = TokenTextSplitter(chunk_size=2048, chunk_overlap=24)
        # 切分器
        docs = text_splitter.split_documents(raw_docs[:])
        # 
        return docs

    def graph_document_text(self, text_chunks):
        """
        
        Uses experimental LLMGraphTransformer to convert unstructured text into a knowledge graph

        Args:
            text_chunks (List): List of document chunks
        """
        llm_transformer = LLMGraphTransformer(llm=self.llm)
        """LLMGraphTransformer 类：这是一个将一系列文档documents转换为graph documents的类。返回一个graph document的列表"""
        graph_docs = llm_transformer.convert_to_graph_documents(text_chunks)
        self.graph.add_graph_documents(
            graph_docs,
            baseEntityLabel=True,
            include_source=True
        )
        # 这里 会围绕 docs 建立一个环绕式的图谱so
        

    def chunk_and_graph(self, raw_docs):
        """
        Breaks the raw text into chunks and converts into a knowledge graph
        将原始的文本分块为知识图谱
        Args:
            raw_docs (str): The raw content extracted from the source
        """
        document_id=[]
        text_chunks = self.chunk_document_text(raw_docs)
        # 先将文档
        if text_chunks is not None:
            print("Making graph (Time Consuming!!!)"," Make graph")
            # 对每一个切片的文档出
            
            self.graph_document_text(text_chunks)

    # def extract_wikipedia_content(self, search_query):
    #     """
    #     Uses the search query and LangChain interface to extract 
    #     content from the results of a Wikipedia search

    #     Args:
    #         search_query (str): The query to search for Wikipedia content on
    #     """
    #     print("Wiki Loader Running",search_query)
    #     raw_docs = WikipediaLoader(query=search_query,load_max_docs=2,doc_content_chars_max=10000).load()
    #     print("Wiki Loaded",raw_docs)
    #     self.chunk_and_graph(raw_docs)

    def graph_text_content(self, path):
        """
        Provided with a text document, will extract and chunk the text
        before generating a graph

        Args:
            path (str): Text document path
        """
        text_docs = TextLoader(path).load()
        print(text_docs)
        self.chunk_and_graph(text_docs)

    def graph_text_documents(self, paths):
        """
        Provided with an array of text documents will extract and
        graph each of them

        Args:
            paths (List): Document paths to extract and graph
        """
        for path in paths:
            self.graph_text_content(path)

    def index_graph(self):
        """
        建立一个index 能够高效索引
        Creates an index on the populated graph tp assist with efficient searches
        """
        self.graph.query(
        "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")

    def reset_graph(self):
        """
        WARNING: Will clear entire graph, use with caution
        """
        self.graph.query(
            """
            MATCH (n)
            DETACH DELETE n
            """
        )
        
# graph_builder=GraphBuilder()
# # print(graph_builder.extract_wikipedia_content("Garmin_Forerunner"))
# print(graph_builder.index_graph())


