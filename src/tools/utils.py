import ast
import inspect
import types
import os


def parse_python_file(file_path):
    """fuck"""
    if file_path[-3:]!=".py":
        return []
    current_file = inspect.getsourcefile(lambda: None)
    # 读取指定文件的内容
   
    with open(file_path, "r") as file:
        file_content = file.read()
    
    # 解析当前文件的 AST
    tree = ast.parse(file_content, filename=current_file)

    # 获取当前模块
    current_module = inspect.getmodule(lambda: None)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            # 使用 exec 动态执行代码并获取函数对象
            local_namespace = {}
            exec(compile(tree, filename=file_path, mode="exec"), {}, local_namespace)
            function_obj = local_namespace.get(function_name, None)
            if isinstance(function_obj, types.FunctionType):
                functions.append((function_name, function_obj))
    return functions
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的目录
current_dir = os.path.dirname(os.path.abspath(current_file_path))
def get_all_functions(function_path=current_dir+"/functions/")->dict:
    files=os.listdir(function_path)
    functions=[]
    for file in files:
        file_path=function_path+"/"+file
        if file[-3:]==".py":
            new_function_list=parse_python_file(file_path)
            functions.extend(new_function_list)
    return dict(functions)


# test=get_all_functions()
# print(test)   
# functions=get_all_functions()
# print(functions[0][1]("fuck"))
