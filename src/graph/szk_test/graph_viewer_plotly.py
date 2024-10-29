from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
from plotly.offline import plot
import os

# 定义函数：可视化特定节点及其符合类型条件的相邻节点
def visualize_neo4j_subgraph(node_identity, node_properties):
    """
    可视化Neo4j中某个节点及其特定类型的相邻节点。

    参数:
    - node_identity: 指定的节点 ID（Neo4j 节点 identity）。
    - node_properties: 限制查询的相邻节点属性类型。

    返回:
    - 一个本地 HTML 文件路径，供用户在浏览器中查看图表。
    """
    # 连接到 Neo4j 数据库
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

    # 处理带空格的标签：用反引号括住标签
    node_properties_escaped = f"`{node_properties}`"

    # 查询该节点及其所有指定类型的直接关联的节点和关系
    query = f"""
    MATCH (n)-[r]-(m)
    WHERE id(n) = {node_identity} AND m:{node_properties_escaped}
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
            node1_type = list(node1.labels)[0] if node1.labels else 'default'  # 转换为列表并获取第一个标签
            G.add_node(node1_id, label=node1_label, node_type=node1_type)  # 添加起始节点
        
        # 检查节点2是否存在
        if node2 is not None:
            node2_id = node2.identity  # 使用 'identity' 作为节点ID
            node2_label = node2['id'] if 'id' in node2 else str(node2.identity)  # 如果'id'属性存在则使用它，否则使用 identity 作为标签
            node2_type = list(node2.labels)[0] if node2.labels else 'default'  # 转换为列表并获取第一个标签
            G.add_node(node2_id, label=node2_label, node_type=node2_type)  # 添加目标节点
        
        # 检查关系是否存在
        if relationship is not None:
            G.add_edge(node1_id, node2_id, label=type(relationship).__name__)  # 添加边，附带关系类型信息

    # 使用 spring 布局让图节点位置更均匀
    pos = nx.spring_layout(G)

    # 自动换行功能：给文本内容加换行符，每隔 5 个字符
    def wrap_text(text, width=2):
        return '\n'.join([text[i:i+width] for i in range(0, len(text), width)])

    # 节点类型对应的颜色
    color_map = {
        'Document': 'blue',
        'Client response': 'green',
        '__Entity__': 'orange',
        'default': 'gray'
    }

    # 提取节点位置和颜色
    x_nodes = [pos[node][0] for node in G.nodes()]  # x 坐标
    y_nodes = [pos[node][1] for node in G.nodes()]  # y 坐标
    node_labels = nx.get_node_attributes(G, 'label')  # 节点标签
    node_types = nx.get_node_attributes(G, 'node_type')  # 节点类型
    node_colors = [color_map.get(node_types[node], 'gray') for node in G.nodes()]  # 为不同类型的节点指定颜色

    # 绘制边
    edge_trace = go.Scatter(
        x=(),
        y=(),
        line=dict(width=3, color='gray'),
        hoverinfo='none',
        mode='lines'
    )

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    # 绘制节点，添加颜色和换行文本
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            color=node_colors,  # 根据节点类型设置颜色
            size=80,  # 调整节点的大小
            colorbar=dict(
                thickness=15,
                title="Node Types",
                xanchor='left',
                titleside='right'
            )
        ),
        text=[wrap_text(node_labels[node], 30) for node in G.nodes()]  # 节点标签内容自动换行
    )

    # 创建图表
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f'Subgraph for Node {node_identity} with {node_properties} neighbors',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        annotations=[dict(
                            text="Node-Edge Graph",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False),
                        height=800,
                        width=800
                    ))
    # 可以直接展示
    # fig.show()
    # 也可以保存图表为 HTML 文件
    file_path = "graph.html"
    plot(fig, filename=file_path, config={'responsive': True})
    # pio.write_html(fig, file=file_path, auto_open=False)
    return file_path  # 返回文件的路径

if __name__ == "__main__":
    node_id = 349  # 需要查询的节点ID
    neighbor_type = "Client response"  # 需要查询的相邻节点类型
    file = visualize_neo4j_subgraph(node_id, neighbor_type)
    print(f"Graph visualization saved to {file}")