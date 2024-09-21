from py2neo import Graph, Node, Relationship,NodeMatcher
 
 
# 连接图库                            初始化账号密码都是neo4j
graph = Graph('http://localhost:7474', auth=('neo4j', 'AI4AI666'))
 
 
# 注意使用Python连接neo4j时要首先启动neo4j的服务，否则Python会抛出异常。
 