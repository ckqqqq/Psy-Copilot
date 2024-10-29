from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
import os
env_path = "/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)

print(os.environ["DEEPSEEK_API_BASE"], os.environ["DEEPSEEK_API_MODEL"])

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "AI4AI666"
test_graph=Neo4jGraph(username="neo4j", password="AI4AI666")
test_graph.query(
            """
            MATCH (n)
            DETACH DELETE n
            """
        )