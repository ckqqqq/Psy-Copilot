
from src.AgentExplain import AgentExplain
from src.ToolPGSQL import ToolPGSQL
from src.Agent import Agent
from src.Formatter import Formatter
from src.AgentExplain import AgentExplain
from src.AgentVisual import AgentVisual
# %%

print("init")
human_input="Bing 和 Start 的dau是多少？"
if "miniapp" not in human_input:
   agent=Agent("dau")
   print("目标为dau")
else:
   agent=Agent("miniapp") 

toolPGSQL=ToolPGSQL(timeout=15)
formatter=Formatter()
agentExplain=AgentExplain()
agentVisual=AgentVisual()
print("SQL generate")

str_query=agent.chat(human_input)
json_query=formatter.json_decode(
    str_query,
    need_key_list=["Analysis","SQL","input","reasoning"]
    )
sql_query=json_query["Analysis"]["SQL"]
sql_query=formatter.schema_table_format(sql_query,err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"],
                                    schema='sapphire',table='sapphire_engagement_metrics_master')
print("PGSQL运行中")
sql_res_df=toolPGSQL.execute_v2(sql_query)
print("PGSQL运行结束",sql_res_df)
sql_table_str=formatter.df_application_id_2_name(sql_res_df)
# response_list.append()
# print(response_list)
print("resoning---")
print(json_query["Analysis"]["reasoning"])
print("code run result---")
print(sql_table_str)
# print("Explain")
# print(agentExplain.explain(query=human_input,sql_result=sql_table_str))
print("Visual")
print(agentVisual.visual(df_csv_format=sql_table_str))