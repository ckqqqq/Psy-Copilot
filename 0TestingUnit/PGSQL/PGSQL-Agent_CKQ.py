import pandas as pd
# pd.set_option('display.max_colwidth', None)

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
#  system_prompt

dau_analysis_sql_query="""SELECT \n    metrics_date,\n    application_id,\n    SUM(CAST(metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION)) AS \"dau\"\nFROM \n    {}.{}\nWHERE metrics_date BETWEEN '2024-06-09' AND '2024-06-09'\n    AND period = 1\n    AND os_version = '#Overall#'\n    AND device_model = '#Overall#'\n    AND client_version = '#Overall#'\n    AND client_build_type = '#Overall#'\n    AND install_channel_l1 = '#Overall#'\n    AND install_channel_l2 = '#Overall#'\n    AND install_channel_l3 = '#Overall#'\n    AND install_channel_l4 = '#Overall#'\n    AND mini_app = ''\n    AND first_launch_source = '#Overall#'\n    AND launch_source = '#Overall#'\n    AND market = '#Overall#'\n    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')\nGROUP BY metrics_date, application_id"""
wau_analysis_sql_query="""SELECT\n    metrics_date AS date,\n    application_id,\n    SUM(CAST(metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION)) AS wau\nFROM\n    {}.{}\nWHERE\n    metrics_date BETWEEN '2024-06-09' AND '2024-06-09'\n    AND period = 7\n    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')\nGROUP BY\n    metrics_date, application_id;"""
mau_analysis_sql_query="SELECT\n    metrics_date AS date,\n    application_id,\n    SUM(CAST(metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION)) AS mau\nFROM\n    {}.{}\nWHERE\n    metrics_date BETWEEN '2024-06-09' AND '2024-06-09'\n    AND period = 30\n    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')\nGROUP BY\n    metrics_date, application_id;"
market_analysis_sql_query="""SELECT\n    market,\n    SUM(CAST(metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION)) AS dau\nFROM\n    {}.{}\nWHERE\n    metrics_date BETWEEN  '2024-06-09' AND '2024-06-09'\n    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')\nGROUP BY\n    market;"""
json_fewshot={
  "DAU_Analysis": [
    {
      "SQL": {
        "query": dau_analysis_sql_query,
      },
      "startdate": "",
      "startdate_ago": "3",
      "enddate": "",
      "enddate_offset": "1",
      "date": "2024-06-09",
      "offset": "1",
      "application_id_list": [
        "2130688B018F4B44BBED68E7A42BBA1E",
        "AE427635ADC245AE973038BCB3D7C21B"
      ],
      "query_conclusion": "获取在2024年6月9日这一天，指定的两个应用程序（Bing-Android和Bing-IOS）的日活跃用户数（DAU）",
      "graph": "柱状图",
      "result_count": "2",
      "additional_metrics": [
        {
          "metric_name": "WAU",
          "description": "在2024年6月9日这一天，Bing APP（Bing-Android和Bing-IOS）的周活跃用户数",
          "SQL": {
            "query":wau_analysis_sql_query,
          }
        },
        {
          "metric_name": "MAU",
          "description": "在2024年6月9日这一天，Bing APP（Bing-Android和Bing-IOS）的月活跃用户数",
          "SQL": {
            "query": mau_analysis_sql_query,
          }
        }
      ],
      "market_analysis": {
        "enabled": True,
        "SQL": {
          "query": market_analysis_sql_query,
        },
        "graph": "饼图",
        "query_conclusion": "在2024年6月9日这一天，获取Bing APP（Bing-Android和Bing-IOS）的不同市场的日活跃用户数分布。"
      }
    }
  ]
}
json_fewshot_str=json.dumps(json_fewshot,ensure_ascii=False)


prompt_dau = """
Context: 
Now we have the user data for some apps, these app are search apps, it intagrated the copilot for AI.
User can also search for information, this app get revenue by ads, and it also have many miniapps for different feature.
We did some AB test based on user interaction data from an app, 
which includes various metrics such as user behavior, codex (AI) behavior, and search behavior. 

The data for each user is structured as a sentence.

The goal is to generate SQL and more information.
The query should focus on：
market:
Format is "en-us",first two is language, last two is country(xl means other counrty that we can not get info.)
Eg."en-us" means American people speak English.

application_id: user will describe a app name, and you need to use id when you serach.
WHEN application_id = '2130688B018F4B44BBED68E7A42BBA1E' THEN 'Bing-Android'
application_id = 'AE427635ADC245AE973038BCB3D7C21B' THEN 'Bing-IOS'
application_id = '4DC5714ABCAD449BA13A9B701A3CF296' THEN 'Start-Android'
application_id = '4A5B528B59954AAE8725B509A41FBF1A' THEN 'Start-IOS' 
application_id = 'F185A93DE6764B098D55089F610A3FB8' THEN 'Copilot-Android'
application_id = 'FC320C411FC12CD4DFBE9A00F3161364' THEN 'Copilot-IOS'
If user did not give you os name, you need to Get Both of them.
Eg."Bing"means ['2130688B018F4B44BBED68E7A42BBA1E','AE427635ADC245AE973038BCB3D7C21B']

metrics_date: if not set in the content, it is today-3, format is "2024-06-07".

dayoffset: If not set in the content, it is 0,only calculate 1 day.

period: 1 for DAU, 7 for WOW, 28 and 30 for MOM

Here is the schema of table:                                                                                                                                                                                                                                                                
umid                 | 1736681
metrics_date         | 2022-09-23
period               | 1
application_id       | 4DC5714ABCAD449BA13A9B701A3CF296
market               | en-in
os_version           | #Overall#
device_model         | #Overall#
client_version       | 23.3.400914606
client_build_type    | #Overall#
install_channel_l1   | #Overall#
install_channel_l2   | #Overall#
install_channel_l3   | #Overall#
install_channel_l4   | #Overall#
mini_app             | 
first_launch_source  | #Overall#
launch_source        | #Overall#
metrics              | {'ActiveUser': {'uu': {'uu': 467.0}, 'msa': {'msa_uu': 0.0}, 'msb': {'msb_uu': 0.0}, 'session': {'session_cnt': 894.0}, 'dwelltime': {'dwelltime': 107686.0, 'dwelltime_uu': 382.0}}}


Output Format: 
Each set of data returns one json, followed by an example based on the provided data.

result_count: How many result will get after query, for example, if group by 2 date and 3 application, it will get 2*3=6 columns.
if you guess the column will more than 100, eg. group by market, please use 100.

Specifications:
- Analyze the input and describe their demand.
- Use these column to identify and describe user demand.
- Provide a detailed and correct pgsql query for each input.
- Limit the output length to avoid excessive verbosity.

Task Examples: 

Input1:
Bing APP一天有多少用户？

Output1:
"""+json_fewshot_str


class Agent():
    def __init__(self):
        self.deployment_name="gpt4"
        self.token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        # replace hardcode api key with credential
        self.client4 = AzureOpenAI(
        #     api_version="2024-02-15-preview",
            api_version="2023-12-01-preview",
            azure_endpoint="https://chatapi-openai.openai.azure.com/",
            azure_ad_token_provider=self.token_provider
        )

    def chat(self,query:str):
        self.messages = self.get_prompt_for_comments([query], prompt_dau)
        # print(str(self.messages))
        # insights = self.get_gpt_response(self.client4, "gpt4", self.messages)
        gpt_response = self.client4.chat.completions.create(
          model="gpt4", # Model = should match the deployment name you chose for your 0125-Preview model deployment
          response_format={ "type": "json_object" },
          messages=self.messages
        )
        insights = gpt_response.choices[0].message.content
        return str(insights)
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
print("agent初始化")
print("-------------------test")
agent=Agent()
gpt_res=agent.chat("帮我们查询一下Bing 和Start两款APP 的dau？")
print(gpt_res)
res_json=json.loads(gpt_res)
with open("test.json","w",encoding="utf-8") as f:
    json.dump(res_json,f,ensure_ascii=False)
print("-------------------")