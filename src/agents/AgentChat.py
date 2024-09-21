from string import Template
import pandas as pd
import os
import json
from openai import OpenAI
from AgentBase import AgentBase

import datetime

class AgentChat(AgentBase):
    """Total design based agent for inherent."""
    def __init__(self,agent_name, model="deepseek-chat", default_api="deepseek", api_key=None, base_url=None, memory_config=None, temperature=0.4, max_tokens=3000, top_p=0.7):
        super().__init__(agent_name,model, default_api, api_key, base_url, memory_config, temperature, max_tokens, top_p)

    # def update_params(self, temperature=None, max_tokens=None, top_p=None):
    #     """
    #     Update the parameters for temperature, max_tokens, and top_p
    #     """
    #     super().update_params(temperature,max_tokens,top_p)

    def chat(self, query: list,is_json=True):
        """
        Interact with the API to get a response for the given query
        """
        response=super().chat(query,is_json)
        return response