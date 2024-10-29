from py2neo import Graph
import networkx as nx
import matplotlib.pyplot as plt

# 连接到Neo4j数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

# 指定特定的节点 identity
node_identity = 330  # 你要查询的特定节点的 identity

# 查询该节点及其所有直接关联的节点和关系
query = f"""
MATCH (n)-[r]-(m)
WHERE id(n) = {node_identity}
RETURN n, r, m
"""

results = graph.run(query)

# 创建 NetworkX 图
G = nx.Graph()

# 遍历查询结果，添加节点和边
for record in results:
    node1 = record['n']
    node2 = record['m']
    relationship = record['r']
    
    # 检查节点1是否存在
    if node1 is not None:
        node1_id = node1.identity  # 使用 'identity' 作为节点ID
        node1_label = node1['id'] if 'id' in node1 else str(node1.identity)  # 如果'id'属性存在则使用它，否则使用 identity 作为标签
        G.add_node(node1_id, label=node1_label)  # 添加起始节点
    
    # 检查节点2是否存在
    if node2 is not None:
        node2_id = node2.identity  # 使用 'identity' 作为节点ID
        node2_label = node2['id'] if 'id' in node2 else str(node2.identity)  # 如果'id'属性存在则使用它，否则使用 identity 作为标签
        G.add_node(node2_id, label=node2_label)  # 添加目标节点
    
    # 检查关系是否存在
    if relationship is not None:
        G.add_edge(node1_id, node2_id, label=type(relationship).__name__)  # 添加边，附带关系类型信息

# 绘制图
plt.figure(figsize=(10, 10))

# 使用 spring 布局让图节点位置更均匀
pos = nx.spring_layout(G)

# 绘制节点和边
node_labels = nx.get_node_attributes(G, 'label')  # 提取节点的标签
nx.draw(G, pos, labels=node_labels, with_labels=True, node_color='skyblue', edge_color='gray', node_size=2000, font_size=10)

# 为边添加标签，即关系类型
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# 保存图为图片并展示
plt.savefig("neo4j_graph.png")  # 保存图片到当前目录
plt.show()  # 展示图片