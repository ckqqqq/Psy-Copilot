from py2neo import Graph
import webbrowser
import urllib.parse
import json

# 定义函数：生成查询语句，并在 Neo4j 浏览器中显示特定节点及其符合类型条件的相邻节点
def visualize_neo4j_subgraph(node_identity, node_properties):
    """
    生成并执行用于在 Neo4j 浏览器中显示指定节点及其特定类型相邻节点的查询。

    参数:
    - node_identity: 指定的节点 ID（Neo4j 节点 identity）。
    - node_properties: 限制查询的相邻节点属性类型。

    返回:
    - 返回生成的 Neo4j 浏览器 URL，并自动打开浏览器展示结果。
    """
    # 连接到 Neo4j 数据库
    graph = Graph("bolt://localhost:7687", auth=("neo4j", "AI4AI666"))

    # 构造查询语句，使用 {node_id} 和 {node_type} 作为参数占位符
    query = """
    MATCH (n)-[r]-(m)
    WHERE id(n) = $node_id AND m:$node_type
    RETURN n, r, m
    """

    # 将查询和参数填充到URL
    encoded_query = urllib.parse.quote(query)
    params = {
        "node_id": node_identity,
        "node_type": node_properties
    }
    encoded_params = urllib.parse.quote(json.dumps(params))

    # 生成 Neo4j 浏览器的 URL (假设 Neo4j 浏览器在本地运行，端口为 7474)
    neo4j_browser_url = f"http://localhost:7474/browser/?query={encoded_query}&params={encoded_params}"

    # 打开浏览器展示结果
    webbrowser.open(neo4j_browser_url)

    # 返回生成的浏览器链接
    return neo4j_browser_url

if __name__ == "__main__":
    node_id = 349  # 需要查询的节点ID
    neighbor_type = "Client response"  # 需要查询的相邻节点类型
    browser_link = visualize_neo4j_subgraph(node_id, neighbor_type)
    print(f"查询已生成并打开，请在浏览器中查看：{browser_link}")