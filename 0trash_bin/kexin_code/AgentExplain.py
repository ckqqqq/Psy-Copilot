import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json

data = [
    ('2024-06-09', 'Bing-Android', 39397464.0),
    ('2024-06-09', 'Bing-IOS', 17309585.0)
]

# 设置列名
columns = ['metrics_date', 'app_name', 'dau']
# 创建 DataFrame
fewshot_df = pd.DataFrame(data, columns=columns)

df_csv_format=fewshot_df.to_csv(index=False)
output_json_format=json.dumps({"explain": "On June 9th,2024, the Bing app had 39,397,464 daily active users (DAU) on Android and 17,309,585 DAU on iOS. To gain deeper insights, consider breaking down the DAU by market to identify which regions are contributing the most."})
system_prompt=f"""
You are a explainer, you can provide useful explaination based on query and result in json format. Here is an example:
Input:
Query: 在2024年6月9日，Bing应用程序针对Android操作系统的日活跃用户数为39,397,464，而对于iOS操作系统的日活跃用户数则为17,309,585。
SQL Result:{df_csv_format}

Please provide an analysis of the SQL Result, including any notable insights or patterns you observe.
Output
{output_json_format}
"""

comments_template = """
Please explain the SQL result based on the query.

Query: {Query}
SQL Result: {ResultValue}

Please provide an analysis of the SQL result, including any notable insights or patterns you observe.
"""
class AgentExplain():
    def __init__(self):
        """针对一个query和一个sql 运行结果 去解释或者分析SQL结果"""
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

    def explain(self, query, df_csv_format: str):
        """
        Interact with the API to explain the query result and return the insights
        """
        try:
            self.messages = self.get_prompt_for_comments(
                system_prompt,
                comments_template.format(Query=query, ResultValue=df_csv_format)
            )
            gpt_response = self.client4.chat.completions.create(
                model="gpt4",  # Model = should match the deployment name you chose for your 0125-Preview model deployment
                response_format={"type": "json_object"},
                messages=self.messages
            )
            insights = gpt_response.choices[0].message.content
            return str(insights)
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