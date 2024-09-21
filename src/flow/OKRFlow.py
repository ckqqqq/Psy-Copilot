from agents.AgentChat import AgentChat 
from OKRPrompts import *
class OKRFlow():
    def __init__(self,agentList:list):
        agentBoss=AgentChat()
        messages=[
            { "role": "system", "content": OKR_SMART_planer_agent["system_prompt"]},
            {"role": "user", "content": "下面是能够使用的各种agent类别，请根据不同Agent的类别和功能进行规划，下面是一个例子：agent"}
            ]
        
        
    def test(self):
        """Observation"""
        pass