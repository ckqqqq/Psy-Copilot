import configparser

config = configparser.ConfigParser()
print(config.read('../setting/config.ini'))
print(config.sections())

import logging
# 实现一个类继承基类

# class CustomAgent(AgentBase):
#     """Custom agent class inheriting from AgentBase."""
#     def __init__(self, model, default_api="deepseek", api_key=None, base_url=None, memory_config=None, temperature=0.4, max_tokens=3000, top_p=0.7):
#         """
#         Initialize CustomAgent class with additional logging setup.
#         """
#         super().__init__(model, default_api, api_key, base_url, memory_config, temperature, max_tokens, top_p)
#         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#         self.logger = logging.getLogger(__name__)

#     def chat(self, messages: list, is_json: bool):
#         """
#         Interact with the API to get a response for the given query and log the interaction.
#         """
#         self.logger.info("Starting chat interaction.")
#         response = super().chat(messages, is_json)
#         self.logger.info("Chat interaction completed.")
        
#         # Additional processing of the response
#         if is_json:
#             try:
#                 response_json = json.loads(response)
#                 self.logger.info("Response is valid JSON.")
#                 return response_json
#             except json.JSONDecodeError:
#                 self.logger.error("Failed to decode JSON response.")
#                 return {"error": "Invalid JSON response"}
#         else:
#             return response

#     def custom_method(self):
#         """
#         Custom method for the CustomAgent class.
#         """
#         self.logger.info("Executing custom method.")
#         # Add custom logic here
#         return "Custom method executed successfully."

# # Example usage
# custom_agent = CustomAgent(model="deepseek-chat", default_api="deepseek")

# print(custom_agent.chat(
#     [{ "role": "system", "content": "你是一个翻译家"},
#     {"role": "user", "content": "阿尼啊赛哟"}], is_json=False))

# print(custom_agent.custom_method())
