from graph_builder_from_json import *
# test=JsonGraphBuilder()
llm=ChatOpenAI(model=os.environ["DEEPSEEK_API_MODEL"], temperature=0,api_key=os.environ["DEEPSEEK_API_KEY"],base_url=os.environ["DEEPSEEK_API_BASE"])
if __name__ == "__main__":
    # # # 调用示例

    graph_builder = JsonGraphBuilder(llm=llm)
    # 可选：创建索引以提高查询效率
    graph_builder.index_graph()
    # 这一步tmd就没跑成功过
"""
SHOW INDEX WHERE name = 'entity'

DROP INDEX index_243dda65

DROP INDEX index_343aff4e

DROP INDEX index_f7700477

DROP INDEX keyword
"""