from string import Template
import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
from src.CodePrompt import init_prompt_miniapp,init_prompt_dau


import datetime

# DefaultAzureCredential()
class Agent():
    def __init__(self, key, temperature=0.4, max_tokens=3000, top_p=0.7):
        """
        Initialize Agent class with API credentials and model parameters
        """
        self.deployment_name = "gpt4"
        self.credential = DefaultAzureCredential()
        self.token_provider = get_bearer_token_provider(
            self.credential, "https://cognitiveservices.azure.com/.default"
        )
        # replace hardcode api key with credential
        self.client4 = AzureOpenAI(
        #     api_version="2024-02-15-preview",
            api_version="2023-12-01-preview",
            azure_endpoint="https://chatapi-openai.openai.azure.com/",
            azure_ad_token_provider=self.token_provider
        )
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        
        if key == "dau":
            self.prompt = init_prompt_dau()
        elif key == "miniapp":
            self.prompt = init_prompt_miniapp()
        else:
            raise ValueError("key must be dau or miniapp")

    def log_call(self, human_input, duration):
        """
        Log the API call details including the time, date, human input, and duration to a log file
        """
        log_filename = "api_call_log.txt"
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"In the SQL query----Time: {current_time}, Duration: {duration:.2f}s, Input: {human_input}\n"
        
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

    def change_prompt(self, key):
        """
        Change the prompt based on the key
        """
        if key == "dau":
            self.prompt = init_prompt_dau()
        elif key == "miniapp":
            self.prompt = init_prompt_miniapp()
        print(key)
        
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

    def chat(self, query: str):
        """
        Interact with the API to get a response for the given query
        """
        self.messages = self.get_prompt_for_comments([query], self.prompt)

        start_time = datetime.datetime.now()

        try:
            gpt_response = self.client4.chat.completions.create(
                model=self.deployment_name,
                response_format={"type": "json_object"},
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )
            insights = gpt_response.choices[0].message.content
        except Exception as e:
            print(f"Error during API call: {e}")
            return "An error occurred while processing your request. Please try again."

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log the API call details
        self.log_call(query, duration)
        
        return str(insights)


    def get_gpt_response(self, client, deployment_name, messages):
        """
        Get GPT response from the API
        """
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p
            )

            if response and response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            else:
                print("Error: No valid response")
                return None
            
        except Exception as e:
            print(f"Error during API call: {e}")
            return None

    #给输入增加prompt
    def get_prompt_for_comments(self,comments, prompt):
        messages = [{ "role": "system", "content": prompt}]
        if isinstance(comments, str):
            messages.append({"role": "user", "content": comments})
        elif isinstance(comments, list):
            for comment in comments:
                messages.append({"role": "user", "content": comment})
        else:
            raise ValueError("comments must be a list or a string.")
            
        return messages
# print("agent初始化")
# print("-------------------test")
# agent=Agent()
# gpt_res=agent.chat("Bing 的dau是多少？")
# print(gpt_res)
# res_json=json.loads(gpt_res)
# with open("test.json","w",encoding="utf-8") as f:
#     json.dump(res_json,f,ensure_ascii=False)
# print("-------------------")