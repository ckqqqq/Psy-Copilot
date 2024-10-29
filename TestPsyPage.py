from src.graph.szk_test.graph_rag_szk import *

from dotenv import load_dotenv
import json

env_path="/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)


#
os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "AI4AI666"

llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
    
graphRAG=GraphRAG(llm=llm)
# graphRAG.structured_retriever("Therapist can use CBT",result_num_limit=50)
retrieved_res=graphRAG.mix_retriever("Therapist can use CBT")
print(retrieved_res)