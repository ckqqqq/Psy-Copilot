

from string import Template
import pandas as pd
import os
import json
from openai import OpenAI
from AgentBase import AgentBase
from tools.utils import *
import datetime

class AgentToolUser(AgentBase):
    """Total design based agent for inherent."""
    def __init__(self, agent_name,model, default_api="deepseek", api_key=None, base_url=None, tools:list=[],memory_config=None, temperature=0.4, max_tokens=3000, top_p=0.7):
        super().__init__(agent_name,model, default_api, api_key, base_url, memory_config, temperature, max_tokens, top_p)
        self.tools=tools
    def add_tool(self,tool:dict):
        """tool example: 
        {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                # s
                "required": ["location"]
            },
            # s
        }
        }
        """
        self.tools.append(tool)

    def del_tool(self,tool_name=None):
        """del tool with a kind of name"""
        self.tools=[i for i in self.tools if i["function"]["name"]!=tool_name]

    def update_params(self, temperature=None, max_tokens=None, top_p=None):
        """
        Update the parameters for temperature, max_tokens, and top_p
        """
        super().update_params(temperature,max_tokens,top_p)

    def chat(self, messages: list,is_json=True):
        """
        Interact with the API to get a response for the given query
        """
        response=super().chat(messages,is_json,tools=self.tools)
        return response
    
agentToolUser=AgentToolUser(agent_name="Test-tool",model="deepseek-coder",default_api="deepseek",tools=[
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
])

res_msg=agentToolUser.chat(messages=[{ "role": "system", "content": "You are a tool user"},
        {"role": "user", "content": "请使用工具告诉我北京的天气"}],is_json=False)
