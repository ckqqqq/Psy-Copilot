from openai import OpenAI
supported_api_list=[
    "deepseek",
]
""""
    "openai",
    "ollama"
"""

import configparser

config = configparser.ConfigParser()
config.read('../config/config.ini')


def getDefaultOpenaiClient(deployment_model:str)-> OpenAI:
    """Supported Models: deepseek:deepseek-chat, deepseek:deepseek-coder,"""
    model=deployment_model
    if model.split(":")[0]=="ollama":
        raise ValueError(f"Your model\source {model} not support. ")
    if model.split(":")[0]=="deepseek":
        base_url="https://api.deepseek.com/beta"
        api_key=config['DEEPSEEK']['DEEPSEEK_API_KEY']
    else:
        raise ValueError(f"Your model\source {model} not support. ")
    return OpenAI(base_url=base_url,api_key=api_key)
def test():
    client=getDefaultOpenaiClient(deployment_model="deepseek:deepseek-chat")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )
    print(response.choices[0].message.content)
        