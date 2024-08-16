# 事实上，直接生成代码是会有风险的，主要因为我们生成的sql 代码过于复杂 ，而其中又有很多变量，目前的效果只能说能跑，但是代码的正确性与fewshot高度相关。

from string import Template
import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
from src.tool_set.tools import tools_list

import datetime
initial_tool_functions="functions=["+",\n".join([tool_function.__doc__ for tool_function in tools_list])+"]"
fewshot0_input="""请告诉我2024年7月15日的daily check结果。"""
fewshot0_output=json.dumps({"reasoning":"""The query requests the daily check result for '2024-7-25'. Therefore, I will utilize the tool tool_daily_check(check_date) to obtain the result.""",
"function_call_result":"""tool_daily_check(check_date="2024-07-15")"""})

fewshot1_input="""请告诉我2024年7月15日的rewards数据。"""
fewshot1_output=json.dumps({"reasoning":"""The provided function calls do not include any functions related to rewards. I should return a Python string containing an explanation.""",
"function_call_result":"""'The provided function calls do not include any functions related to rewards.'"""})

system_prompt=Template("""
As a tool user, you can utilize the useful provided python functions to answer the question. Please generate Python code to call the function or provide an string explanation if provided functions is not enough for solving problems. Anwser with json format.
There are functions:
$functions
                       
There are some examples:
Input:
$fewshot0_input
Output:
$fewshot0_output                  
Input:
$fewshot1_input
Output:
$fewshot1_output                   
""").substitute(functions=initial_tool_functions,fewshot0_input=fewshot0_input,fewshot0_output=fewshot0_output,fewshot1_input=fewshot1_input,fewshot1_output=fewshot1_output)

comments_template = Template("""
Please utilize the useful provided python functions to answer the question.

Input:
$query
""")

class AgentToolUser():
    def __init__(self,tool_functions=initial_tool_functions):
        """Select and use tools from tool set"""
        self.deployment_name="gpt4"
        self.credential = AzureCliCredential()
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
        self.system_prompt=system_prompt
        self.comments_template=comments_template

    
    def log_call(self, human_input, duration):
        """
        Log the API call details including the time, date, human input, and duration to a log file
        """
        log_filename = "api_call_log.txt"
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"In the Explain----Time: {current_time}, Duration: {duration:.2f}s, Input: {human_input}\n"
        
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

    def run_code(self,function_call_code:str):
        global_vars = {}
        local_vars = {}
        try:
            exec("""from src.tool_set.tools import * \nfunction_call_result="""+function_call_code, global_vars, local_vars)
            function_call_res = local_vars['function_call_result']
            return function_call_res
        except Exception as e:
            print(f"Error during API interaction: {e}")
            return "Run GPT's Code error."

    def use_tool(self,query):
        """
        Use the selected tool to process the input query and return the result
        """

        start_time = datetime.datetime.now()

        try:
            self.messages=self.get_prompt_for_comments(
                self.system_prompt,
                self.comments_template.substitute(query=query))
            gpt_response = self.client4.chat.completions.create(
            model="gpt4", # Model = should match the deployment name you chose for your 0125-Preview model deployment
            response_format={ "type": "json_object" },
            messages=self.messages
            )
            response_str = gpt_response.choices[0].message.content
            # print("生成回复候选列表长度为",len(gpt_response.choices))
            response_json=json.loads(response_str)
            function_call_result=self.run_code(response_json["function_call_result"])
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            # Log the API call details
            self.log_call(query+str(function_call_result), duration)
            return function_call_result
        except Exception as e:
            print(f"Error during API interaction: {e}")
            return "An error occurred while processing your request. Please try again."

    def get_gpt_response(self,client, deployment_name, messages):
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=0.7,
                max_tokens=3000,  # Adjusted for potentially longer responses
                top_p=1
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
    def get_prompt_for_comments(self, system_prompt,comments):
        messages = [{ "role": "system", "content": system_prompt}]
        if isinstance(comments, str):
            messages.append({"role": "user", "content": comments})
        elif isinstance(comments, list):
            for comment in comments:
                messages.append({"role": "user", "content": comment})
        else:
            raise ValueError("comments must be a list or a string.")
        return messages
# print("Tool set",tools_list)
# # function_call_res=exec()
# global_vars = {}
# local_vars = {}
# exec("""
# from src.tool_set.tools import *
# function_call_result=tool_daily_check(check_date="2024-07-11")
# """, global_vars, local_vars)
# function_call_res = local_vars['function_call_result']
# # print(result)  # 输出 30
# print(function_call_res) 