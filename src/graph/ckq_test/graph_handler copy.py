from py2neo import Graph, NodeMatcher,RelationshipMatcher
# 连接到 Neo4j 数据库

class Graph_Handler():
    def __init__(self,url="bolt://localhost:7687",auth=("neo4j", "AI4AI666")):
        self.graph = Graph(url, auth=auth)
    def test_query(self):
        node_id = "cfaa55090780b600f50e095d4cbd4755"
        # node_id=330
        query = f"""
        MATCH (n:Document)
        WHERE n.id = '{node_id}'
        RETURN n
        """     
        # id: dd8ccca04754bc9dc28625811a1a053e
        res=self.graph.run(query)
        print(res)
    def test_query2(self):
        node_id = r"The Therapist'S Suggestions Can Stimulate Productive Introspection".replace("'", "\\'")
        # 小心单引号
        # node_id=330
        query = f"""
        MATCH (n)
        WHERE n.id = '{node_id}'
        RETURN n
        """     
        # id: dd8ccca04754bc9dc28625811a1a053e
        res=self.graph.run(query)
        print(res,type(res))
    
        
test=Graph_Handler()
test.test_query2()
# 写query的时候有几个要点，
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#     def test_node():
# # Create a node representing a person
#         person = Node("Person 测试节点", name="大人")
#         self.graph.create(person)

# # Create a node representing a movie
# movie = Node("Movie", title="电影")
# graph.create(movie)
# # Create a relationship between the person and the movie
# person_movie = Relationship(person, "LOVES", movie)
# graph.create(person_movie)
# # 创建 NodeMatcher 对象
# matcher = NodeMatcher(graph)

# # 查询所有类别为 Psychotherapy 的节点
# psychotherapy_nodes = matcher.match("Psychotherapy").all()
# rel_matcher = RelationshipMatcher(graph)
# # 打印结果
# for node in psychotherapy_nodes:
#     print(list(node.values())[0])
    # print(type(node))
    # print(node.values())