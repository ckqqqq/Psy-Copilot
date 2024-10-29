import os
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
env_path="/home/ckqsudo/code2024/Psy-Agent/src/config/.env"
load_dotenv(env_path)
messages = [
                (
                    "system",
                    "You are a helpful translator. Translate the user sentence to French.",
                ),
                ("human", "I love programming."),
            ]
llm = ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
print(ai_msg)