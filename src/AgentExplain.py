import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json
from string import Template
import datetime
fewshot_input="""请告诉我这几天的dau的变化。"""
fewshot_reasoning="""The query is asking for the Daily Active Users (DAU) for the Bing application on both iOS and Android platforms for the last 7 days from the specified metrics_date, which is July 7, 2024. The SQL query will include conditions for the two application IDs related to Bing (one for iOS and one for Android) and will span the 7 days leading up to and including July 7, 2024. The query should also return the metrics_date alongside the DAU count and use default values for all other fields."""
fewshot_input_sql_res_csv_format=pd.DataFrame({
    'metrics_date': ['2024-06-30', '2024-07-01', '2024-07-02', '2024-07-03', '2024-07-04', '2024-07-05', '2024-07-06', '2024-07-07'],
    'dau': [3464428, 3563268, 3611328, 3570606, 3487081, 3439577, 3256525, 3230524]
}).to_csv(index=False)
fewshot_explain="""From June 30th to July 7th, 2024, Bing experienced a fluctuation in daily active users (DAU). ** The DAU started at 3,464,428 on June 30th and saw a slight increase over the first three days, peaking at 3,611,328 on July 2nd. Afterwards, there was a gradual decline with minor ups and downs until it reached the lowest count of 3,230,524 on July 7th.** \nThe overall trend suggests a decrease in DAU towards the end of the 8-day period. This decrease in daily users could be due to various factors,** such as changes in user behavior, seasonal effects, or competition from other apps.** **Further analysis might involve looking at the prior weeks,** any marketing campaigns that might have influenced the numbers, or events that could have impacted user engagement."""

system_prompt=Template("""
You are a explainer, you can provide useful explaination based on query and result in json format. Please provide an analysis of the SQL Result, including any notable insights or patterns you observe. Please wrap important insight with '**' in json value. Here is an example:
Input:

Query: $fewshot_query
SQL Result: $fewshot_sql_res


Output:
                       
$fewshot_explain
""").substitute(fewshot_query=" ".join([fewshot_input,fewshot_reasoning]),fewshot_sql_res=fewshot_input_sql_res_csv_format,fewshot_explain=json.dumps({"explain": fewshot_explain}))

comments_template = Template("""
Please explain the SQL result based on the query.

Query: $input_query
SQL Result: $input_sql_res

Please provide an analysis of the SQL result, including any notable insights or patterns you observe.
""")
class AgentExplain():
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
        log_entry = f"In the Explain----Time: {current_time}, Duration: {duration:.2f}s, Input: {human_input}\n"
        
        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)

    def explain(self,query,df_csv_format:str):
        """
        Interact with the API to explain the query result and return the insights
        """

        start_time = datetime.datetime.now()

        try:
            self.messages=self.get_prompt_for_comments(
                system_prompt,
                comments_template.substitute(input_query=query,input_sql_res=df_csv_format))
            gpt_response = self.client4.chat.completions.create(
            model="gpt4", # Model = should match the deployment name you chose for your 0125-Preview model deployment
            response_format={ "type": "json_object" },
            messages=self.messages
            )
            insights = gpt_response.choices[0].message.content
            print("生成回复候选列表长度为",len(gpt_response.choices))
        except Exception as e:
            print(f"Error during API interaction: {e}")
            return "An error occurred while processing your request. Please try again."

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log the API call details
        self.log_call(query, duration)
        
        return insights

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
# agentExplain=AgentExplain()
# print(agentExplain.explain("Bing最近7天的dau是多少？",""",metrics_date,dau
# 0,2024-06-26,3972708
# 1,2024-06-27,3815117
# 2,2024-06-28,3742047
# 3,2024-06-29,3468826
# 4,2024-06-30,3464428
# 5,2024-07-01,3563268
# 6,2024-07-02,3611329
# """))