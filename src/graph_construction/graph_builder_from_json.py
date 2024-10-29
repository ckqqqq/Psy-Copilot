from locale import setlocale
from multiprocessing import process
import os
import json
from typing import List
from altair import themes
from flask import sessions
from langchain.text_splitter import TokenTextSplitter
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from create_unstructured_prompt import create_unstructured_prompt_for_psy_insight
from hashlib import md5
from copy import deepcopy


from langchain_community.graphs.neo4j_graph import BASE_ENTITY_LABEL,_remove_backticks
# langchain 只能用这种简单的东西
from langchain_community.graphs.graph_document import Node,Relationship,GraphDocument
# langchain 还能用最基本的定义，用于和之前的代码统一，其他的都是狗屎
from dotenv import load_dotenv
from typing import List
from graph_document_cache import GraphDocumentCacheManager
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
        """这个Neo4j其实也是封装的一层 py2neo"""
        self.graph = Neo4jGraph(username="neo4j", password="AI4AI666")
        self.llm = llm
        self.counter=0
        self.graph_document_cache=GraphDocumentCacheManager()
    # def _get_node_import_query(self) -> str: 
    #     """langchain的官方代码，能够批量建立节点的Neo4j数据库执行脚本，"""
    #     return (
    #         "UNWIND $data AS row "
    #         "MERGE (source {id: row.id}) "
    #         "SET source += {type: row.type} "
    #         "SET source += row.properties "
    #         "SET source:`{label}` "  # 使用标签表达式为节点设置标签
    #         "RETURN source.id AS id"
    #     )
    def _get_node_import_query(self) -> str: 
        """langchain的官方代码，能够批量建立节点的Neo4j数据库执行脚本"UNWIND $data AS row "
            "CALL apoc.merge.node([row.type], {id: row.id}, "
            "row.properties, {}) YIELD node """
        return (
            "UNWIND $data AS row "
            f"CALL apoc.merge.node([row.type], {{id: row.id}}, row.properties) YIELD node "
            "RETURN node.id AS id"
        )
        # return (
        #     "UNWIND $data AS row "
        #     f"MERGE (source:`{BASE_ENTITY_LABEL}` {{id: row.id}}) "
        #     "SET source += row.properties "
        #     "WITH source, row "
        #     "CALL apoc.create.addLabels( source, [row.type] ) YIELD node "
        #     "RETURN node.id AS id"
        # )# 可以将type这样的标签作为Labels加进去
    def _get_id(self,content) -> str:
        """基于对话按照顺序生成一个六位数id，添加到每个topic的字典中，放在最前面，从中文开始编码，从000001开始"""
        self.counter+=1
        return str(self.counter).zfill(6)
    
    def create_node(self,node_list:List[Node]):
        """
        批量建立节点，传入一个节点列表，将列表中节点载入进neo4j中，注意对于id为空的节点不会创建
        其中一个为langchain定义的节点Node，包含下列信息
        :param id: 节点的唯一标识符
        :param type: 节点的类型
        :param properties: 节点的属性字典
        :return: 创建的节点id列表
        """
        data = [
                {
                    "id": node.id,# id是唯一标识符
                    "type": node.type, #type 是类别
                    "properties": node.properties # properties 是一个属性字典
                } for node in node_list
            ]
        node_import_query = self._get_node_import_query()# 这里还是用的langchain官方的实现，因为目前还不清楚__entity__的含义
        return self.graph.query(
            node_import_query,
            {
                "data": data,
            },
        )
    def add_attribute_to_node(self, node_id, attribute_name, attribute_value):
        # 基于唯一标识符匹配节点，为节点增添属性# 使用节点的id属性进行匹配# 使用参数化查询设置属性，Cyber语法规定，点的后面不能有$符号，所以适当使用python中 f"{value}"是有益的 这里好像有问题哦
        query = (
            f"""MATCH (n) 
            WHERE n.id = $node_id   
            SET n.{attribute_name} = $attribute_value   
            RETURN n"""
        )
        return self.graph.query(
            query,
            {
                "node_id": node_id,
                "attribute_value": attribute_value
            },
        )
        
    def create_relation(self, source_id, target_id, rel_type, properties={}):
        """
        创建两个节点之间的关系，并包含指定的属性，注意，对于id为空的节点不会创建。
        :param source_id: 源节点的唯一标识符
        :param target_id: 目标节点的唯一标识符
        :param rel_type: 关系的类型
        :param properties: 关系的属性字典
        :return: 创建的关系对象
        """
        if target_id=="" or source_id=="":
            return
        # short label 
        else:
            # 我让kimi写的最简单的代码
            query = f"""
                MATCH (a), (b) WHERE a.id = $node1_id AND b.id = $node2_id
                MERGE (a)-[:{rel_type}]->(b)
                RETURN distinct 'done'
                """
            return self.graph.query(
                query,
                {
                    "node1_id": source_id,
                    "node2_id": target_id
                },
            )

    def build_graph_from_psy_insight_json_files(self, file_paths: List[str],limit_session_number=None) -> List[dict]:
        """
        载入所有json文件
         Args:
            file_paths (List[str]):json文件路径的列表。
        """
        json_data_list = []
        for path in file_paths:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                json_data_list.append(data)
        session_cnt=0
        for json_data in json_data_list:
            for session_unit in json_data:
                session_cnt+=1
                self.psy_insight_unit_into_graph(session_unit) 
                if limit_session_number and session_cnt>=limit_session_number:
                    print("会话session",session_cnt)
                    return        
    def extract_psy_insight_dialog(self,dialog_history,num_limit=30,both_side=True):
        """如果both_side=True那么双方的对话内容都会拼接，否则只拼接Seeker的"""
        line_list=[u["speaker"]+" "+u["content"] for u in dialog_history if both_side or u["speaker"]=="Seeker"]
        text="\n".join(line_list[:num_limit])
        return text

    def psy_insight_unit_into_graph(self, session_unit):
        """
        将单个键值对插入到知识图谱中。
        Args:
            key (str):json数据的键，作为查询。
            value (dict):json数据的值，作为内容。这里的value是数据集中的一个单元吗
        """
        # 注意，这里的node 只是字符串格式的限定节点
        D_ID=session_unit["dialog_id"]
        # 对话文本 节点
        origin_dialog_text=json.dumps(session_unit["dialog"], ensure_ascii=False)
        # 对每个对话记录
        # D_ID=self._get_id(dialog)
        pure_dialog_history=self.extract_psy_insight_dialog(dialog_history=session_unit["dialog"],num_limit=40,both_side=True)
        pure_seeker=self.extract_psy_insight_dialog(dialog_history=session_unit["dialog"],num_limit=10,both_side=False)
        # 新建对话节点
        dialog_node=Node(id="dialog"+D_ID,type="dialog",
        properties={"type":"dialog","text":pure_dialog_history,"origin_dialog":origin_dialog_text,"content":pure_seeker})
        # 所有短标签文本的id都是内容
        background_text=session_unit["background"]
        # 建立字符串节点
        background_node=Node(id="background"+D_ID,type="background",properties={"text":background_text,"chat_stage":session_unit["stage"],"label_length":"long_label"})
        # 单独处理诸如 background 这种长描述标签

        
        # 正式写入节点入图
        self.create_node([dialog_node,background_node])
        # 建立dialog与这些标签的联系
        self.create_relation(dialog_node.id,background_node.id,"background")
        # 批量处理短标签文本
        short_label_list=[
            "theme","psychotherapy","topic"]
        for label in short_label_list:
            if label in session_unit and session_unit[label]!="":
                node_id=session_unit[label]
                # 正式建立节点
                self.create_node([Node(id=node_id,type=label,properties={"text":node_id,"label_length":"short_label"})])
                # 建立关系
                self.create_relation(dialog_node.id,node_id,rel_type=label)
        
        # 处理较长文本节点，将其制作为基于文档的知识图谱
        
        ## 知识图谱的实体节点名称
        self.node_labels=[
        "client_emotion",
        "therapist_strategy",
        "client_action",
        "target",
        "psychotherapy",
        "client_response",
        "therapist_response",
        "client_issue",
        "client_background",
        "therapist_guide",
        "dialog_topic"
        ]
        ## 知识图谱的关系名称
        self.rel_types=["Explain","Evaluate","Intent to","Relieve","Help","Respond","Prevent","Be_Crucial_For","Prompt"]
        # 存储session中的key和node中的类别名称
        long_label_types = [
            # "reasoning", 
            "guide",
            "summary"
        ]

        # 处理长标签，将其转为文档并创建知识图谱，返回
        for long_label_type in long_label_types:
            
            # 获得长标签的文本
            long_label_text=session_unit[long_label_type]
            # 跳过空标签
            if session_unit[long_label_type]=="":
                continue
            # 获得文档节点的id
            node_id_list = self.process_document_for_graph(long_label_text, dialog_id=long_label_type + D_ID)
            # 对每个文档节点建立其与dialog的联系
            for node_id in node_id_list:
                self.add_attribute_to_node(node_id,attribute_name="label_length",attribute_value="long_label")
                self.create_relation(dialog_node.id, node_id, long_label_type)
        return 
    def chunk_document_text(self, docs: List):
        """
        将文档列表进行分块处理。
        Args:
            docs (List): 文档对象的列表。
        Returns:
            List: 分块后的文档列表。
        """
        print("Splitting text into chunks...")
        text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=24)
        chunks = text_splitter.split_documents(docs)
        return chunks
    
    def process_document_for_graph(self,document_text:str,dialog_id:str):
        """
            将文档进行处理
        """
        # 将文本转换为 LangChain 的 Document 对象
        from langchain.schema import Document
        doc = Document(page_content=document_text)
        # 分块处理文档
        text_chunk_docs = self.chunk_document_text([doc])
        print("文档分片后数量",len(text_chunk_docs))
        node_id_list=[]
        if text_chunk_docs:
            for idx,doc in enumerate(text_chunk_docs):
                print("文档",idx,"对话ID",dialog_id)
                doc_id=doc.metadata["id"]="document"+str(idx)+dialog_id
                node_id_list.append(doc_id)
            # 建立知识图谱，注意源文件的node_id就是document的id，也是节点的id
            self.graph_document_text(text_chunk_docs,doc_id)
            return node_id_list

    def graph_document_text(self, text_chunks: List,doc_id:str):
        """
        使用 LLMGraphTransformer 将文本块转换为知识图谱。
        Args:
            text_chunks (List): 分块后的文档列表。
        """
        print("Transforming text chunks into graph documents...")
        
        cache_graph_docs=self.graph_document_cache.get_graph_document(doc_id)
        if cache_graph_docs:
            print("load",doc_id)
            graph_docs=cache_graph_docs.deepcopy()
        else:
            # 使用特定prompt
            chat_prompt=create_unstructured_prompt_for_psy_insight(node_labels=self.node_labels,rel_types=self.rel_types)
            # 定义节点构建器
            print("允许节点",self.node_labels,"允许关系",self.rel_types)
            llm_transformer = LLMGraphTransformer(llm=self.llm,prompt=chat_prompt,allowed_nodes=self.node_labels,allowed_relationships=self.rel_types,strict_mode=False,node_properties=False,relationship_properties=False)#  进行节点构建和关系构建得到GraphDocument 列表，这个类是langchain定义的一个包含nodes relations 和原始Document类
            
            # 建立知识图谱，注意源文件的node_id就是document的id，也是节点的id
            graph_docs = llm_transformer.convert_to_graph_documents(text_chunks)
            for idx,graph_doc in enumerate(graph_docs):
                if isinstance(graph_doc,GraphDocument):
                    for y,node in enumerate(graph_doc.nodes):
                        graph_docs[idx].nodes[y].properties["text"]=graph_docs[idx].nodes[y].id
                        graph_docs[idx].nodes[y].properties["label_length"]="short_label"
                        # 注意标识所有的短标签
            self.graph_document_cache.add_or_update_graph_document(doc_id,graph_docs)
            # 将知识图谱存入cache
                
        
        
        
        # 将这个GraphDocument 在neo4j中绘制
        self.graph.add_graph_documents(
            graph_docs,
            baseEntityLabel=True,
            include_source=True
            # include_source：如果需要用mention连接 document及其相关实体，这个参数就是True
        )

    def index_graph(self):
        """
        创建图的索引，以提高查询效率。 __Entity__ 的作用在这里，e 是节点的别名，__Entity__ 是节点的标签,e:是别名的意思，就是langchain的那个Stupid标签。
        """
        # DROP INDEX IF EXISTS node_id_index 这是一种删除索引的方式
        
        # 建立一个全文索引，能够通过文本匹配模糊查找某些信息
        
        
        self.graph.query(
            "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]"
        )
        # 建立一个精确匹配的索引，对于所有有id属性的节点建立，用于快速定位节点
        # 建立短标签的索引

        self.graph.query(
            "CREATE INDEX  FOR (n:Node) ON (n.id)"
        )
        #        self.graph.query(
        # """CALL db.index.fulltext.createNodeIndex("dialog_pure_seeker_index", ["dialog"], ["id"], {analyzer: "standard"})
        # entiti似乎没必要orz
        
        # self.graph.query(
        #     "CREATE INDEX short_label FOR (n:Node) ON (n.id)"
        # )
        self.graph.query(
        """CALL db.index.fulltext.createNodeIndex("dialog_pure_seeker_index", ["dialog"], ["id"], {analyzer: "standard"})
        """
        )
        # self.graph.query(
        #     """
        #     CREATE FULLTEXT INDEX node_id_index IF NOT EXISTS 
        #     FOR (n) 
        #     ON (n.id) 
        #     WHERE EXISTS(n.label_length) AND n.label_length = 'short_label'
        #     """
        # )
        # 建立短标签索引，段标签的id就是标签信息

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
        
   
    
llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])

if __name__ == "__main__":
    # # # 调用示例

    graph_builder = JsonGraphBuilder(llm=llm)
    import os
    test_path="/home/ckqsudo/code2024/0dataset/psy-insight-for-graph"
    json_file_paths=[
        "/home/ckqsudo/code2024/0dataset/psy-insight-for-graph/en_data7.json",
        # 英文数据集和中文数据集
        "/home/ckqsudo/code2024/0dataset/psy-insight-for-graph/cn_data7.json"]
    graph_builder.build_graph_from_psy_insight_json_files(json_file_paths,limit_session_number=1000)

    # 可选：创建索引以提高查询效率
    graph_builder.index_graph()
    # 这一步tmd就没跑成功过

    # 没用了就清除所有的内容
    # graph_builder.reset_graph()
