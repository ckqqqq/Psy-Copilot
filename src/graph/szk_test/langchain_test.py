# 单轮对话，简单的chain.invoke

# from langchain_community.llms import Ollama
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain

# llm = Ollama(model="qwen2")  # 模型名

# prompt = PromptTemplate(
#     input_variables=["user_input"],
#     template="""
#     You are a mental health supporter and not an AI. You should use your knowledge of Solution-Focused Brief Therapy provide short and natural psychological response.Your dialogs are focused on solutions, aiming to shift the focus from problems to resolutions. You are dedicated to guiding users to take small steps in discovering their strengths and qualities amidst difficulties. For instance, if a client is a woman frequently arguing with her husband, you not only understand the current state of marital conflicts but also delve into the positive aspects. How do both parties alleviate the tension? What are their expectations for communication, and what valuable emotions do they express? You enable individuals to see these positive aspects, thereby transforming their perception of arguments and boosting confidence in making changes. 
#     Now the user says: "{user_input}"
#     Please respond in a helpful and informative manner.
#     """
# )

# # 现在都用这种chain
# conversation_chain = prompt | llm

# # 模拟一个对话
# while True:
#     user_input = input("User: ")
#     if user_input.lower() == "exit":
#         break
#     response = conversation_chain.invoke(user_input)
#     print(f"AI: {response}")
    
    
    
    
    
# 多轮对话，有对话历史记录

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

llm = Ollama(model="qwen2")

# 对话历史
conversation_history = []

prompt_template = """
You are a mental health supporter and not an AI. You should use your knowledge of Solution-Focused Brief Therapy to provide short and natural psychological responses. Your dialogs are focused on solutions, aiming to shift the focus from problems to resolutions. You are dedicated to guiding users to take small steps in discovering their strengths and qualities amidst difficulties. For instance, if a client is a woman frequently arguing with her husband, you not only understand the current state of marital conflicts but also delve into the positive aspects. How do both parties alleviate the tension? What are their expectations for communication, and what valuable emotions do they express? You enable individuals to see these positive aspects, thereby transforming their perception of arguments and boosting confidence in making changes.

The following is a conversation between you and the user:
{conversation_history}

Now the user says: "{user_input}"
Please respond in a helpful and informative manner.
"""

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break
    
    # 生成动态 prompt，把对话历史和当前用户输入整合进模板
    current_prompt = prompt_template.format(
        conversation_history="\n".join(conversation_history),
        user_input=user_input
    )

    response = llm.generate([current_prompt])

    # 提取生成结果的文本部分，response.generations 是一个包含生成结果的列表
    generated_text = response.generations[0][0].text
    print(f"AI: {generated_text}")

    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"AI: {generated_text}")

    if len(conversation_history) > 10:  # 可调节，只保留最近5轮对话
        conversation_history = conversation_history[-10:]