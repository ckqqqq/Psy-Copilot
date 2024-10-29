# from py2neo import Graph, Node
from langchain_community.graphs.graph_document import GraphDocument,Node,Relationship

from langchain_community.graphs import Neo4jGraph
# 
from langchain_community.graphs.neo4j_graph import BASE_ENTITY_LABEL,_remove_backticks
from langchain_community.graphs.graph_document import Node,Relationship


from dotenv import load_dotenv
import os
env_path = "/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

print(os.environ["DEEPSEEK_API_BASE"], os.environ["DEEPSEEK_API_MODEL"])

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "AI4AI666"


class Graph_Handler():
    def __init__(self, username="neo4j", password="AI4AI666"):
        self.graph = Neo4jGraph(username=username, password=password)
    def _get_node_import_query(self) -> str: 
        # 建立和根节点的索引联系
            return (
                "UNWIND $data AS row "
                f"MERGE (source:`{BASE_ENTITY_LABEL}` {{id: row.id}}) "
                "SET source += row.properties "
                "WITH source, row "
                "CALL apoc.create.addLabels( source, [row.type] ) YIELD node "
                "RETURN distinct 'done' AS result"
            )
        # """"CALL apoc.merge.node([row.type], {id: row.id}, "
        #         "row.properties, {}) YIELD node "
        # """
    def _get_rel_import_query(self,baseEntityLabel:bool=False) -> str:
        """屎山代码"""
        if baseEntityLabel:
            return (
                "UNWIND $data AS row "
                f"MATCH (source:`{BASE_ENTITY_LABEL}` {{id: row.source}}) "
                f"MATCH (target:`{BASE_ENTITY_LABEL}` {{id: row.target}}) "
                "WITH source, target, row "
                "CALL apoc.merge.relationship(source, row.type, "
                "{}, row.properties, target) YIELD rel "
                "RETURN distinct 'done'"
            )
            # 建立索引的形式
        else:
            return (
                "UNWIND $data AS row "
                "CALL apoc.merge.node([row.source_label], {id: row.source},"
                "{}, {}) YIELD node as source "
                "CALL apoc.merge.node([row.target_label], {id: row.target},"
                "{}, {}) YIELD node as target "
                "CALL apoc.merge.relationship(source, row.type, "
                "{}, row.properties, target) YIELD rel "
                "RETURN distinct 'done'"
            )
    
    def create_node(self,node:Node):
        """
        创建一个新节点，并包含指定的属性。
        :param id: 节点的唯一标识符
        :param type: 节点的类型
        :param properties: 节点的属性字典
        :return: 创建的节点对象
        """
        data = [
                {
                    "id": node.id,
                    "type": node.type,
                    "properties": node.properties
                }
            ]
        node_import_query = self._get_node_import_query()# 这里还是用的langchain官方的实现，因为目前还不清楚__entity__的含义
        return self.graph.query(
            node_import_query,
            {
                "data": data,
            },
        )
        # return new_node
    
    def langchain_relation(self, relation:Relationship):
        """
        创建两个节点之间的关系，并包含指定的属性。langchain 官方的实现，恕我直言，简直是屎山

        :param source_id: 源节点的唯一标识符
        :param target_id: 目标节点的唯一标识符
        :param rel_type: 关系的类型
        :param properties: 关系的属性字典
        :param source_label: 源节点的标签（默认为 BASE_ENTITY_LABEL）
        :param target_label: 目标节点的标签（默认为 BASE_ENTITY_LABEL）
        :return: 创建的关系对象
        """
        data = [
            {
                "source": relation.source.id,
                "source_label": _remove_backticks(relation.source.type),
                "target": relation.target.id,
                "target_label": _remove_backticks(relation.target.type),
                "type": _remove_backticks(
                    relation.type.replace(" ", "_").upper()
                ),
                "properties": relation.properties,
            }
        ]
        rel_import_query = self._get_rel_import_query()
        
        return self.graph.query(
            rel_import_query,
            {
                "data": data,
            },
        )
    
    def create_relation(self, source_id, target_id, rel_type, properties={}):
        """
        创建两个节点之间的关系，并包含指定的属性。
        :param source_id: 源节点的唯一标识符
        :param target_id: 目标节点的唯一标识符
        :param rel_type: 关系的类型
        :param properties: 关系的属性字典
        :return: 创建的关系对象
        """
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

    def find_node_by_id(self,node_id="dd8ccca04754bc9dc28625811a1a053e"):
        node_id=node_id.replace("'", "\\'")
        query = f"""
        MATCH (n)
        WHERE n.id = '{node_id}'
        RETURN n
        """
        return self.graph.query(query)
    
# 示例用法
# target_node=Node(id="8861c1b39ba576b67412a34b68cbfdfb",type="Document",properties={})
# test_node=Node(id="test5",type="test5",properties={})
test_node=Node(id="test9",type="Fuck",properties={})
# test_rel=Relationship(source=test_node,target=target_node,type="test_relationship_doc",properties={})
test=Graph_Handler()

res=test.find_node_by_id('b5e9550d5542165a6bdea52b8fc07bf4')
print(res)
print(test.find_node_by_id('test6'))
res=test.relationship2('b5e9550d5542165a6bdea52b8fc07bf4','test6',"ffff")
print(res)
