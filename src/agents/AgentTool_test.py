import sys
import os


# 添加包的根目录到 sys.path
sys.path.append("/home/ckqsudo/code2024/Psy-Agent/src/")

from AgentToolUser import *

# print(res_msg)
function_dict=get_all_functions()
tool = res_msg.tool_calls[0]
# functions_list=
# res_msg.model_dump_jsom
# print(res.tool_calls[0])
func=res_msg.model_dump_json()
print(function_dict)
print(tool.id)
print(tool.function.name)
print(function_dict[tool.function.name](tool.function.arguments))