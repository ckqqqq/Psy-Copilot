from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import os

# 定义函数：可视化特定节点及其符合类型条件的相邻节点
import networkx as nx

from py2neo import Graph

"""
可视化Neo4j中某个节点及其特定类型的相邻节点，递归深度为2。

参数:
- node_identity: 指定的节点 ID（Neo4j 节点 identity）。
- node_properties: 限制查询的相邻节点属性类型。
- depth: 递归深度，默认为2。

返回:
- plotly.graph_objs.Figure 对象，供用户在 Jupyter Notebook 或其他环境中查看图表。
"""
node_identity=330
constraint_node_properties="ALL"
depth=2
# 连接到 Neo4j 数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

# 处理带空格的标签：用反引号括住标签
node_properties_escaped = f"`{constraint_node_properties}`"

# 查询该节点及其所有指定类型的直接关联的节点和关系
if constraint_node_properties == "ALL":
    query = f"""
    MATCH p=(n)-[*1..{depth}]-(m)
    WHERE id(n) = {node_identity}
    RETURN nodes(p), relationships(p)
    """
else:
    query = f"""
    MATCH p=(n)-[*1..{depth}]-(m)
    WHERE id(n) = {node_identity} AND ALL(node IN nodes(p) WHERE node:{node_properties_escaped})
    RETURN nodes(p), relationships(p)
    """

results = graph.run(query)
 # 遍历查询结果，添加节点和边
for record in results:
    nodes = record['nodes(p)']
    relationships = record['relationships(p)']
    
    # 添加节点
    for node in nodes:
        print(type(node.labels))
        print(list(node.labels))
        for item in list(node.labels):
            print(item)
        # print(list(node.labels)[1])