import streamlit as st
# Step 2: 导入所需模块
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI


def get_response():
    # Step 3: 获取 Azure CLI 凭据
    credential = DefaultAzureCredential()

    # Step 4: 获取 Azure OpenAI 客户端
    token_provider = lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token

    client = AzureOpenAI(
        api_version="2023-12-01-preview",
        azure_endpoint="https://chatapi-openai.openai.azure.com",
        azure_ad_token_provider=token_provider
    )

    # Step 5: 使用 Azure OpenAI 客户端
    # 替换为适当的调用 Azure OpenAI API 的代码，例如：
    response = client.chat.completions.create(
        model="gpt4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me a joke."}
        ]
    )

    # Step 6: 打印 API 响应
    print(response)
    return response

st.write("""
# My first app
Hello *world!*
""")

if st.button("Get Resource Groups"):
    try:
        res = get_response()
        st.write(f"Resource Group: {res}")
    except Exception as e:
        st.error(f"Error: {str(e)}")