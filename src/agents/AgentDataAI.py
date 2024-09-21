from AgentBase import AgentBase
from _AgentUtils_ import getDefaultOpenaiClient
from pandasai import Agent
from typing import List
import pandas as pd

class AgentDataAI():
    def __init__(self,agent_name,model="deepseek-chat",default_api="deepseek",api_key=None,base_url=None,memory_config=None, temperature=0.4, max_tokens=3000, top_p=0.7,data_lake:List[pd.DataFrame]=[]):
        """pandasai is a Excellent project for asking pandas data"""
        super().__init__(agent_name,model, default_api, api_key, base_url, memory_config, temperature, max_tokens, top_p)
        self.agent=Agent(dfs=data_lake,config={"llm",self.client},memory_size=10)
        # self.agent=Agent(dfs=data_lake,config={"llm": self.llm})
        
        
    def chat(self,query:str):
        response=self.agent.chat(query)
        print(response)
        return response