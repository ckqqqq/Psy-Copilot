
from AgentExplain import AgentExplain
from ToolPGSQL import ToolPGSQL
from Agent import Agent
from Formatter import Formatter
from AgentExplain import AgentExplain
# %%

print("init")
agent=Agent("miniapp")
toolPGSQL=ToolPGSQL(timeout=15)
formatter=Formatter()
agentExplain=AgentExplain()
print("SQL generate")
human_input="dau排名前十的miniapp有哪些？"
str_query=agent.chat(human_input)
json_query=formatter.json_decode(
    str_query,
    need_key_list=["Analysis","SQL","input","reasoning"]
    )
sql_query=json_query["Analysis"]["SQL"]
sql_query=formatter.schema_table_format(sql_query,err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"],
                                    schema='sapphire',table='sapphire_engagement_metrics_master')
response_list=[sql_query]
print("PGSQL运行中")
sql_res,col_names=toolPGSQL.execute(sql_query)
print("PGSQL运行结束")
sql_table_str=formatter.sql_output_format(sql_res,col_names)
# response_list.append()
# print(response_list)
print("resoning")
print(json_query["Analysis"]["reasoning"])
print("sql_result")
print(sql_table_str)
print("Explain")
print(agentExplain.explain(query=human_input,sql_result=sql_table_str))