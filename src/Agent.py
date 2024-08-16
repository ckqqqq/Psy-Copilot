from string import Template
import pandas as pd
import os
import json
from openai import OpenAI


import datetime
"""
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)
"""
# DefaultAzureCredential()

openai_api_key = os.getenv("OPENAI_API_KEY")
model_list=["gpt-4o-mini","deepseek-chat"]
chatbot_url_list=['https://gptnb.keqichen.top/v1','https://api.deepseek.com']
class Agent():
    def __init__(self, key=openai_api_key,base_url=chatbot_url_list[1],model=model_list[1], temperature=0.4, max_tokens=3000, top_p=0.7):
        """
        Initialize Agent class with API credentials and model parameters
        """
        self.model = model
        # replace hardcode api key with credential
        self.client4 = OpenAI(base_url=base_url,api_key=openai_api_key)
        self.system_prompt="You are a professional therapist, and you are good at counseling."
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        

    def log_call(self, human_input, duration):
        """
        Log the API call details including the time, date, human input, and duration to a log file
        """
        log_filename = "api_call_log.txt"
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"--Time: {current_time}, Duration: {duration:.2f}s, Input: {human_input}\n"
        
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

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
        self.messages = self.get_prompt_for_comments(system_prompt=self.system_prompt,user_comments=[query])

        start_time = datetime.datetime.now()

        try:
            gpt_response = self.client4.chat.completions.create(
                model=self.model,
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
    def get_prompt_for_comments(self,system_prompt,user_comments):
        messages = [{ "role": "system", "content": system_prompt}]
        if isinstance(user_comments, str):
            messages.append({"role": "user", "content": user_comments})
        elif isinstance(user_comments, list):
            for comment in user_comments:
                messages.append({"role": "user", "content": comment})
        else:
            raise ValueError("comments must be a list or a string.")
            
        return messages
# print("agent初始化")
# print("-------------------test")
# agent=Agent()
# gpt_res=agent.chat("你是谁")
# print(gpt_res)
# print(gpt_res)
# res_json=json.loads(gpt_res)
# with open("test.json","w",encoding="utf-8") as f:
#     json.dump(res_json,f,ensure_ascii=False)
# print("-------------------")