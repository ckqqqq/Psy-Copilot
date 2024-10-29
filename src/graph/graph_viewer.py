from py2neo import Graph
import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import os

def visualize_neo4j_subgraph(node_identity, constraint_node_properties, depth=1, max_nodes=25):
    """
    可视化Neo4j中某个节点及其特定类型的相邻节点，支持避免环路的情况下递归查询邻居节点，并限制显示节点的数量。
    
    参数:
    - node_identity: 指定的节点 ID（Neo4j 节点 identity）。
    - constraint_node_properties: 限制查询的相邻节点属性类型。
    - depth: 递归深度，默认为1（1为邻居，2为二级邻居）。
    - max_nodes: 图中显示的最大节点数量，默认为25。

    返回:
    - plotly.graph_objs.Figure 对象，供用户在 Jupyter Notebook 或其他环境中查看图表。
    """
    # 连接到 Neo4j 数据库
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

    # 处理带空格的标签：用反引号括住标签
    node_properties_escaped = f"`{constraint_node_properties}`"



    # 查询该节点及其所有指定类型的直接关联的节点和关系，避免死循环，递归查找节点
        # 修改后的查询部分
    if constraint_node_properties == "ALL":
        query = f"""

        // 获取目标节点的直接邻居
        MATCH p1=(n)-[*1..1]-(m)
        WHERE n.id = $target_node_id
        RETURN nodes(p1) AS nodes, relationships(p1) AS relationships
        UNION
        // 对于标签为 Document 的直接邻居，获取它们的 __Entity__ 邻居之间的关系
        MATCH (n)-[]-(m:Document)-[]-(d:__Entity__)
        MATCH (d)-[r]-(e:__Entity__)
        WHERE n.id = $target_node_id AND d.id <> e.id
        RETURN [d, e] AS nodes, [r] AS relationships
        UNION
        // 对于标签为 dialog 的直接邻居，获取它们的邻居节点及其与 dialog 的关系
        MATCH (n)-[r1]-(m:dialog)-[r2]-(d)
        WHERE n.id = $target_node_id
        RETURN [m, d] AS nodes, [r1, r2] AS relationships
        """
    else:
        raise ValueError("不支持哦")
        
        


    results = graph.run(query, target_node_id=node_identity)

    # 创建 NetworkX 图
    G = nx.Graph()

    # 记录当前添加的节点数
    current_node_count = 0
    
    
    
    """假设 node_identity 是某个节点的 id，并且图中有以下路径：

路径 1: A -> B -> C

路径 2: A -> D

那么 results 可能看起来像这样：所以首尾可能是跟节点
[
    (['A', 'B', 'C'], [('A', 'B'), ('B', 'C')]),
    (['A', 'D'], [('A', 'D')])
]
    """
    # 使用字典追踪已访问的节点，避免重复访问，并记录每个节点的层次，这个字典是下面这个循环的关键，用于记录节点的层次的同时追踪已经访问的节点，每个访问的节点都会在这里存储一次
    visited_nodes = {}  # 形式: {node_id: {'label': label,  'node_type': type}}
    # 遍历查询结果，添加节点和边
    for record in results:
        nodes = record['nodes']
        relationships = record['relationships']
        # 获取得到的点对和，这个点可能是根-一级节点，也可能是跟-二级节点
        
        # 优先加入dialog节点或者文档节点
        nodes_sorted =nodes
        # 排序的依据是节点的 labels 属性中是否同时不包含 'dialog' 和 'Document'。如果一个节点的标签中既不包含 'dialog' 也不包含 'Document'，那么它在排序后的结果中会被放在更前面（因为 True 在布尔排序中被视为小于 False）。 h

        # 添加节点
        for node in nodes_sorted:
            # 这里的node.identity为一个int变量
            node_id = node.identity  # 使用 'identity' 作为节点ID
            node_label = node['id'] if 'id' in node else str(node.identity)  # 如果'id'属性存在则使用它，否则使用 identity 作为标签
            
            node_text= node['text'] if 'text' in node else str(node_label) # 如果text 文字标签存在则使用它，否则使用id显示
            
            label_list = list(node.labels) if node.labels else ['default']# 节点的多个标签
            
            
            if node_id not in visited_nodes:
                #  如果该节点还没有被访问过，则将其加入字典中
                if current_node_count >= max_nodes:
                    break #

                if "__Entity__" in label_list and len(label_list) > 1:
                    node_type = (set(label_list) - {"__Entity__"}).pop()
                else:
                    node_type = "__Entity__" if "__Entity__" in label_list else label_list[0]

                # 标记为
                visited_nodes[node_id] = {'label': node_label, 'node_type': node_type}
                
                G.add_node(node_id, label=node_label, node_type=node_type,node_text=node_text)  # 添加访问次数为1

                current_node_count += 1  # 增加节点计数


        # 添加边
        for relationship in relationships:
            start_node = relationship.start_node
            end_node = relationship.end_node
            if "__Entity__" in start_node.labels and "__Entity__" in end_node.labels:
                print(relationship)
                is_cot=True
            else:
                is_cot=False
            G.add_edge(start_node.identity, end_node.identity, label=type(relationship).__name__,is_cot=is_cot)  # 添加边，附带关系类型信息

        # 如果节点数量达到最大值，则停止循环
        if current_node_count >= max_nodes:
            break

    # 使用 spring 布局让图节点位置更均匀
    # pos = nx.spring_layout(G)

    pos=nx.shell_layout(G)
    # 自动换行功能：给文本内容加换行符，每隔 5 个字符
    def wrap_text(text, width=8,text_clip_num=20):
        if len(text)>text_clip_num:
            text=text[:16]
            text+="..."
        width = len(text) // 2 + 1 if len(text) > width else width
        return '<br>'.join([text[i:i + width] for i in range(0, len(text), width)])

    # 节点类型对应的颜色，新增不同层级的节点颜色
    color_map = {
        'Client_emotion': 'rgba(255, 165, 0, 0.5)',  # 浅橙色，半透明
        'Therapist_strategy': 'rgba(0, 255, 0, 0.5)',  # 浅吕色，半透明
        'Client_action': 'rgba(255, 192, 203, 0.5)',  # 浅粉色，半透明
        'Target': 'rgba(128, 0, 128, 0.5)',  # 浅紫色，半透明
        'Psychotherapy': 'rgba(255, 105, 180, 0.5)',  # 浅粉红色，半透明
        'Client_response': 'rgba(122, 255, 0, 0.5)',  # 浅绿色，半透明
        'Therapist_response': 'rgba(0, 128, 128, 0.5)',  # 浅蓝绿色，半透明
        'Client_issue': 'rgba(255, 255, 0, 0.5)',  # 浅黄色，半透明
        'Client_background': 'rgba(100, 0, 3, 0.5)',  # 浅灰色，半透明
        'Therapist_guide': 'rgba(255, 215, 0, 0.5)',  # 浅金色，半透明
        'Dialog_topic': 'rgba(135, 206, 235, 0.5)',  # 天空蓝色，半透明
        'Document': 'rgba(135, 96, 235, 0.5)',
        'background': 'rgba(100, 0, 3, 0.5)',  # 浅灰色，半透明
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
    node_types = nx.get_node_attributes(G, 'node_type')  # 节点类型
    # 为不同层级和类型的节点指定颜色
    node_hover_texts=nx.get_node_attributes(G, 'node_text')
    
    node_hover_text_dict={}
    node_colors = [] # 获取颜色列表
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
    is_cot_list=[]
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
        is_cot=G.get_edge_data(edge[0], edge[1])['is_cot']
        edge_text_labels.append(relationship_label)
        is_cot_list.append(is_cot)

    # 创建边的 Scatter 对象
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=3, color='rgba(211, 211, 211, 0.4)'),  # 透明的浅白色
        hoverinfo='none',
        mode='lines'
    )

    # 创建关系文字的 Scatter 对象
    edge_text_trace = go.Scatter(
        x=edge_text_x,
        y=edge_text_y,
        text=edge_text_labels,  # 显示关系类型
        mode='text',
        textfont=dict(size=10, color='rgba(0, 0, 0, 0.9)'),  # 设置文字大小和颜色
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
            size=[60 for node in G.nodes()],  # 不需要设置
            colorbar=dict(
                thickness=15,
                title="Node Types",
                xanchor='left',
                titleside='right'
            )
        ),
        text=[wrap_text(node_labels[node]) for node in G.nodes()],  # 节点上显示的标签
        hovertext=[node_hover_texts[node] for node in G.nodes()],  # 悬停时显示节点类型和层级
        textfont=dict(color='rgb(0, 0, 0)', size=10),  # 设置文字大小
    )

    # 创建图表
    fig = go.Figure(data=[edge_trace, edge_text_trace, node_trace],
                    layout=go.Layout(
                        # title=f'Subgraph for Psy-COT',
                        # title_font=dict(size=32),  # 设置标题字体大小
                        showlegend=True,  # 显示图例
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        
                        xaxis=dict(showgrid=False, zeroline=False),
                        yaxis=dict(showgrid=False, zeroline=False),
                        height=800,
                        width=800,
                    ))

    # 添加图例
    for node_type, color in color_map.items():
        
        # print(node_type)
        fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                name=node_type,
                showlegend=True
        ))

    return fig  # 返回 plotly.graph_objs.Figure 对象