import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
import string
from code_editor import code_editor
import datetime

# 创建 DataFrame

input_df_csv_format=pd.DataFrame([
    ('2024-06-09', 'Bing-Android', 39397464.0),
    ('2024-06-09', 'Bing-IOS', 17309585.0)
], columns= ['metrics_date', 'app_name', 'dau']).to_csv(index=False)
output_json_format=json.dumps(
"""
{
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: 'bar'
    }
  ]
}
""")
system_prompt=f"""
You are a code expert, you can provide useful transformation from pandas dataframe data to appropriate parameters json item for visualization function. Please provide an useful organization of chart setting json. Here is an example:
Input Data: 
{input_df_csv_format}

Output:
{output_json_format}
"""

comments_template = string.Template("""
Here is a suggestion $human_instruction Please provide an useful organization of chart setting json.:

Input Data: $df_csv_format

Output:
""")
class AgentVisual():
    def __init__(self):
        """针对一个query和一个sql 运行结果 去解释或者分析SQL结果"""
        self.deployment_name="gpt4"
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

    
    def log_call(self, human_input, duration):
        """
        Log the API call details including the time, date, human input, and duration to a log file
        """
        log_filename = "api_call_log.txt"
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"In the Visualization----Time: {current_time}, Duration: {duration:.2f}s, Input: {human_input}\n"
        
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)


    def visual(self,human_instruction,df_csv_format:str):
        """
        self.messages=self.get_prompt_for_comments(
            system_prompt,
            comments_template.format(Query=query,ResultValue=df_csv_format))
        gpt_response = self.client4.chat.completions.create(
          model="gpt4", # Model = should match the deployment name you chose for your 0125-Preview model deployment
          response_format={ "type": "json_object" },
          messages=self.messages
        )
        insights = gpt_response.choices[0].message.content
        return str(insights)
        """
        
        start_time = datetime.datetime.now()
        self.messages=self.get_prompt_for_comments(
            system_prompt,
            comments_template.substitute(human_instruction=human_instruction,df_csv_format=df_csv_format))
        # print(self.messages)
        
        gpt_response = self.client4.chat.completions.create(
          model="gpt4", # Model = should match the deployment name you chose for your 0125-Preview model deployment
          response_format={ "type": "json_object"},
          messages=self.messages
        )
        insights = gpt_response.choices[0].message.content

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log the API call details
        self.log_call(human_instruction, duration)

        return insights
    #与API交互，返回结果
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
# agentVisual=AgentVisual()
# print(agentVisual.visual(input_df_csv_format))