import os
import json
from typing import List
from langchain.text_splitter import TokenTextSplitter
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

env_path = "/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

print(os.environ["DEEPSEEK_API_BASE"], os.environ["DEEPSEEK_API_MODEL"])

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "AI4AI666"

class JsonGraphBuilder:
    """
    改写后的类可用于从本地json文件构建Neo4j知识图谱
    该类能够加载多个json文件，将每个key作为query，value作为content，插入到知识图谱中
    """

    def __init__(self, llm):
        
        self.graph = Neo4jGraph(username="neo4j", password="AI4AI666")
        self.llm = llm

    def load_json_files(self, file_paths: List[str]) -> List[dict]:
        """
        加载多个json文件，并返回所有文件的数据列表。
        Args:
            file_paths (List[str]):json文件路径的列表。
        Returns:
            List[dict]: 包含每个json文件数据的列表。
        """
        json_data_list = []
        for path in file_paths:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_data_list.append(data)
        return json_data_list

    def process_json_data(self, json_data_list: List[dict]):
        """
        处理加载的json数据，将每个键值对插入知识图谱。
        Args:
            json_data_list (List[dict]): 包含每个json文件数据的列表。
        """
        for json_data in json_data_list:
            for key, value in json_data.items():
                self.insert_key_value_into_graph(key, value)

    def insert_key_value_into_graph(self, key: str, value: dict):
        """
        将单个键值对插入到知识图谱中。
        Args:
            key (str):json数据的键，作为查询。
            value (dict):json数据的值，作为内容。
        """
        # 将key和value组合成一个文档
        document_text = f"Query: {key}\nContent: {json.dumps(value, ensure_ascii=False)}"
        # 将文本转换为 LangChain 的 Document 对象
        from langchain.schema import Document
        doc = Document(page_content=document_text)

        # 分块处理文档
        text_chunks = self.chunk_document_text([doc])
        if text_chunks:
            self.graph_document_text(text_chunks)

    def chunk_document_text(self, docs: List):
        """
        将文档列表进行分块处理。
        Args:
            docs (List): 文档对象的列表。
        Returns:
            List: 分块后的文档列表。
        """
        print("Splitting text into chunks...")
        text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
        chunks = text_splitter.split_documents(docs)
        return chunks

    def graph_document_text(self, text_chunks: List):
        """
        使用 LLMGraphTransformer 将文本块转换为知识图谱。
        Args:
            text_chunks (List): 分块后的文档列表。
        """
        graph_prompt = """
        这里写一个prompt即可
        """
        print("Transforming text chunks into graph documents...")
        llm_transformer = LLMGraphTransformer(llm=self.llm, prompt=graph_prompt)
        # 这里加上prompt
        graph_docs = llm_transformer.convert_to_graph_documents(text_chunks)
        self.graph.add_graph_documents(
            graph_docs,
            baseEntityLabel=True,
            include_source=True
        )

    def build_graph_from_json_files(self, file_paths: List[str]):
        """
        从多个json文件构建知识图谱。
        Args:
            file_paths (List[str]):json文件路径的列表。
        """
        json_data_list = self.load_json_files(file_paths)
        self.process_json_data(json_data_list)

    def index_graph(self):
        """
        创建图的索引，以提高查询效率。
        """
        self.graph.query(
            "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]"
        )

    def reset_graph(self):
        """
        清空整个知识图谱。
        """
        self.graph.query(
            """
            MATCH (n)
            DETACH DELETE n
            """
        )

if __name__ == "__main__":
    # 调用示例
    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
    graph_builder = JsonGraphBuilder(llm=llm)
    import os
    test_path="/home/ckqsudo/code2024/0dataset/key_value"
    json_file_paths=[]
    for file_name in os.listdir(test_path):
        if file_name.endswith(".json"):
            print(file_name)
            json_file_paths.append(test_path+"/"+file_name)
    graph_builder.build_graph_from_json_files(json_file_paths)

    # 可选：创建索引以提高查询效率
    graph_builder.index_graph()

    # 没用了就清除所有的内容
    # graph_builder.reset_graph()
