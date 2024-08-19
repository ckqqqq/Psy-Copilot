import _AgentUtils_
from string import Template
import pandas as pd
import os
import json
from openai import OpenAI


import datetime

class AgentBase():
    """Total design based agent for inherent."""
    def __init__(self,model,default_api="deepseek",api_key=None,base_url=None, temperature=0.4, max_tokens=3000, top_p=0.7):
        """
        Initialize Agent class with API credentials and model parameters
        """
        self.model=model
        self.temperature,self.max_tokens,self.top_p=temperature,max_tokens,top_p
        if default_api in _AgentUtils_.supported_api_list and api_key==None and base_url==None:
            self.client=_AgentUtils_.getDefaultOpenaiClient("deepseek:deepseek-chat")
        else:
            self.client=OpenAI(api_key=api_key,base_url=base_url)

    def update_params(self, temperature=None, max_tokens=None, top_p=None):
        """
        Update the parameters for temperature, max_tokens, and top_p
        """
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if top_p is not None:
            self.top_p = top_p

    def chat(self, system_prompt:str ,query: str):
        """
        Interact with the API to get a response for the given query
        """

        start_time = datetime.datetime.now()
        try:
            gpt_response = self.client.chat.completions.create(
                model=self.model,
                response_format=None,     
                messages=[
                { "role": "system", "content": system_prompt},
                {"role": "user", "content": query}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            insights = gpt_response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            return "An error occurred while processing your request. Please try again."
        duration = (datetime.datetime.now() - start_time).total_seconds()
        return str(insights)
    
agentTest=AgentBase(model="deepseek-chat",default_api="deepseek")

print(agentTest.chat("你是一个翻译家","Hi,阿尼啊赛哟"))

