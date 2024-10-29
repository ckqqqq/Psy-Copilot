from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import os

import json
import os
from collections import deque
from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go

CACHE_FILE = 'graph_cache.json'  # 缓存文件路径
MAX_CACHE_SIZE = 20  # 缓存中最多存储的条目数

def load_cache():
    """加载缓存文件，如果不存在则创建一个空缓存"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"cache_order": [], "cache_data": {}}

def save_cache(cache):
    """将缓存保存到文件"""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False)

def cache_key(node_identity, constraint_node_properties, depth, max_nodes):
    """生成缓存 key（用于索引缓存中的图结构）"""
    return f"{node_identity}_{constraint_node_properties}_{depth}_{max_nodes}"

def check_cache(node_identity, constraint_node_properties, depth, max_nodes):
    """检查缓存是否有指定的图数据"""
    cache = load_cache()
    key = cache_key(node_identity, constraint_node_properties, depth, max_nodes)
    if key in cache["cache_data"]:
        return cache["cache_data"][key]
    return None

def update_cache(node_identity, constraint_node_properties, depth, max_nodes, graph_data):
    """更新缓存，添加新的图数据并确保缓存大小不超过限制"""
    cache = load_cache()
    key = cache_key(node_identity, constraint_node_properties, depth, max_nodes)
    
    # 如果缓存已经有20条记录，删除最早的记录（先进先出）
    if len(cache["cache_order"]) >= MAX_CACHE_SIZE:
        oldest_key = cache["cache_order"].pop(0)  # 移除最早的 key
        cache["cache_data"].pop(oldest_key)  # 从 cache_data 中移除该条记录
    
    # 添加新的缓存条目
    cache["cache_order"].append(key)
    cache["cache_data"][key] = graph_data
    
    # 保存缓存到文件
    save_cache(cache)

def visualize_neo4j_subgraph(node_identity, constraint_node_properties, depth=1, max_nodes=25,use_cache=False):
    """
    可视化Neo4j中某个节点及其特定类型的相邻节点，支持避免环路的情况下递归查询邻居节点，并限制显示节点的数量。
    使用缓存机制避免重复查询。
    """
    # 首先检查缓存中是否已有该图结构
    cached_result = check_cache(node_identity, constraint_node_properties, depth, max_nodes)
    
    if cached_result and use_cache:
        print("使用缓存数据绘制图")
        # 使用缓存数据，恢复图结构
        G = nx.node_link_graph(cached_result)  # 从缓存中的图结构恢复 NetworkX 图
    else:
        print("查询 Neo4j 并缓存结果")
        # 连接到 Neo4j 数据库
        graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

        # 处理带空格的标签：用反引号括住标签
        node_properties_escaped = f"`{constraint_node_properties}`"

        # 使用字典追踪已访问的节点，避免重复访问，并记录每个节点的层次
        visited_nodes = {}

        # 查询该节点及其所有指定类型的直接关联的节点和关系，避免死循环
        if constraint_node_properties == "ALL":
            query = f"""
            MATCH p=(n)-[*1..{depth}]-(m)
            WHERE n.id = $target_node_id
            RETURN nodes(p), relationships(p)
            """
        else:
            query = f"""
            MATCH p=(n)-[*1..{depth}]-(m)
            WHERE n.id = $target_node_id AND ALL(node IN nodes(p) WHERE node:{node_properties_escaped})
            RETURN nodes(p), relationships(p)
            """

        results = graph.run(query, target_node_id=node_identity)

        # 创建 NetworkX 图
        G = nx.Graph()

        # 记录当前添加的节点数
        current_node_count = 0

        # 遍历查询结果，添加节点和边
        for record in results:
            nodes = record['nodes(p)']
            relationships = record['relationships(p)']
            nodes_sorted = sorted(nodes, key=lambda node: (('dialog' not in node.labels) and ('Document' not in node.labels)))

            # 添加节点
            for node in nodes_sorted:
                node_id = node.identity
                node_label = node['id'] if 'id' in node else str(node.identity)
                label_list = list(node.labels) if node.labels else ['default']

                if node_id not in visited_nodes:
                    if current_node_count >= max_nodes:
                        break

                    if "__Entity__" in label_list and len(label_list) > 1:
                        node_type = next(label for label in label_list if label != "__Entity__")
                    else:
                        node_type = "__Entity__" if "__Entity__" in label_list else label_list[0]

                    visited_nodes[node_id] = {'label': node_label, 'level': 1, 'node_type': node_type}
                    G.add_node(node_id, label=node_label, node_type=node_type, level=1)

                    current_node_count += 1

                elif node_id in visited_nodes and visited_nodes[node_id]['level'] < 2:
                    if node_id == node_identity:
                        continue
                    visited_nodes[node_id]['level'] = 2
                    G.nodes[node_id]['level'] = 2

            for relationship in relationships:
                start_node = relationship.start_node
                end_node = relationship.end_node
                G.add_edge(start_node.identity, end_node.identity, label=type(relationship).__name__)

            if current_node_count >= max_nodes:
                break

        # 缓存图结构
        graph_data = nx.node_link_data(G)  # 将 NetworkX 图转换为可序列化的 JSON 数据
        update_cache(node_identity, constraint_node_properties, depth, max_nodes, graph_data)

    # 使用 spring 布局让图节点位置更均匀
    pos = nx.spring_layout(G)

    # 自动换行功能：给文本内容加换行符，每隔 5 个字符
    def wrap_text(text, width=20):
        width = len(text) // 2 + 1 if len(text) > width else width
        return '<br>'.join([text[i:i + width] for i in range(0, len(text), width)])

    # 节点类型对应的颜色，新增不同层级的节点颜色
    color_map = {
        'Client action': 'rgba(255, 192, 203, 0.5)',  # 浅粉色，半透明
        'Client emotion': 'rgba(255, 165, 0, 0.5)',  # 浅橙色，半透明
        'Client issue': 'rgba(255, 255, 0, 0.5)',  # 浅黄色，半透明
        'Client response': 'rgba(0, 255, 0, 0.5)',  # 浅绿色，半透明
        'Client strategy': 'rgba(0, 255, 255, 0.5)',  # 浅青色，半透明
        'Document': 'rgba(0, 0, 255, 0.5)',  # 浅蓝色，半透明
        'Targetpsychotherapy': 'rgba(128, 0, 128, 0.5)',  # 浅紫色，半透明
        'Therapist action': 'rgba(255, 0, 255, 0.5)',  # 浅洋红色，半透明
        'Therapist response': 'rgba(0, 128, 128, 0.5)',  # 浅蓝绿色，半透明
        'Therapist strategy': 'rgba(128, 128, 0, 0.5)',  # 浅橄榄色，半透明
        'background': 'rgba(192, 192, 192, 0.5)',  # 浅灰色，半透明
        'dialog': 'rgba(135, 206, 235, 0.5)',  # 天空蓝色，半透明
        'guide': 'rgba(255, 215, 0, 0.5)',  # 浅金色，半透明
        'psychotherapy': 'rgba(255, 105, 180, 0.5)',  # 浅粉红色，半透明
        'stage': 'rgba(75, 0, 130, 0.5)',  # 深紫色，半透明
        'topic': 'rgba(255, 165, 0, 0.5)',  # 浅橙色，半透明
        '__Entity__': 'rgba(128, 128, 128, 0.5)',  # 默认实体为浅灰色
    }

    # 提取节点位置和颜色
    x_nodes = [pos[node][0] for node in G.nodes()]  # x 坐标
    y_nodes = [pos[node][1] for node in G.nodes()]  # y 坐标

    node_labels = nx.get_node_attributes(G, 'label')  # 节点标签
    node_levels = nx.get_node_attributes(G, 'level')  # 节点层级
    node_types = nx.get_node_attributes(G, 'node_type')  # 节点类型

    # 为不同层级和类型的节点指定颜色
    node_colors = []
    for node in G.nodes():
        node_type = node_types.get(node, '__Entity__')  # 如果未定义节点类型，使用默认类型 '__Entity__'
        node_colors.append(color_map.get(node_type, 'gray'))
        
    # 初始化边的坐标
    edge_x = []
    edge_y = []

    # 初始化边的关系文字坐标和文字
    edge_text_x = []
    edge_text_y = []
    edge_text_labels = []

    # 遍历边，添加边和关系类型
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        # 追加边的坐标信息
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        # 计算边的中点
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2

        # 在边的中点添加关系文字坐标和内容
        edge_text_x.append(mid_x)
        edge_text_y.append(mid_y)

        # 获取关系类型文字
        relationship_label = G.get_edge_data(edge[0], edge[1])['label']
        edge_text_labels.append(relationship_label)

    # 创建边的 Scatter 对象
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=3, color='rgba(211, 211, 211, 0.5)'),  # 透明的浅白色
        hoverinfo='none',
        mode='lines'
    )

    # 创建关系文字的 Scatter 对象
    edge_text_trace = go.Scatter(
        x=edge_text_x,
        y=edge_text_y,
        text=edge_text_labels,  # 显示关系类型
        mode='text',
        textfont=dict(size=10, color='rgba(200, 150, 200, 0.9)'),  # 设置文字大小和颜色
        hoverinfo='none'
    )

    # 绘制节点，添加颜色和换行文本
    node_trace = go.Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color=node_colors,  # 根据节点层级和类型设置颜色
            size=[50 if node_levels[node] == 1 else 70 for node in G.nodes()],  # 一级节点大于二级节点
            colorbar=dict(
                thickness=15,
                title="Node Types",
                xanchor='left',
                titleside='right'
            )
        ),
        text=[wrap_text(node_labels[node]) for node in G.nodes()],  # 节点上显示的标签
        hovertext=[f"Type: {node_types[node]} - Level: {1 if node_levels[node] == 2 else 2}" for node in G.nodes()],  # 悬停时显示节点类型和层级
        textfont=dict(color='rgb(0, 0, 0)', size=10),  # 设置文字大小
    )

    # 创建图表
    fig = go.Figure(data=[edge_trace, edge_text_trace, node_trace],
                    layout=go.Layout(
                        # title=f'Subgraph for Node {node_identity} with {constraint_node_properties} neighbors (Depth: {depth})',
                        # title_font=dict(size=32),  # 设置标题字体大小
                        showlegend=True,  # 显示图例
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
                        width=800,
                    ))

    # 添加图例
    for node_type, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=node_type,
            showlegend=True
        ))

    return fig  # 返回 plotly.graph_objs.Figure 对象