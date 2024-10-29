from graph_builder_from_json import *


test=JsonGraphBuilder(llm=llm)
res=test.create_node([Node(id="10086",type="check_id"),Node(id="10087",type="check_id_2"),Node(id="",type="check_id_2"),Node(id="",type="check_id_2")])
print(res)