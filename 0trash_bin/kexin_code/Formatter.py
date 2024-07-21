import json
import pandas as pd
class Formatter():
    def __init__(self):
        # Bingviz 
        self.app_ids=['2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B', '4DC5714ABCAD449BA13A9B701A3CF296', '4A5B528B59954AAE8725B509A41FBF1A', 'F185A93DE6764B098D55089F610A3FB8', 'FC320C411FC12CD4DFBE9A00F3161364']
        self.app_names=['Bing-Android', 'Bing-IOS', 'Start-Android', 'Start-IOS', 'Copilot-Android', 'Copilot-IOS']
        # 2130688B018F4B44BBED68E7A42BBA1E
    def app_id_2_name(self,i_str:str):
        id2name=dict(zip(self.app_ids,self.app_names))
        for app_id in id2name.keys():
            if app_id in i_str:
                i_str=i_str.replace(app_id,id2name[app_id])
        return i_str
    def df_application_id_2_name(self,df:pd.DataFrame):
        if 'application_id' in df.columns:
            id2name=dict(zip(self.app_ids,self.app_names))
            # 请确保这个id一定要全
            df.rename(columns={'application_id': 'app_name'}, inplace=True)
            df['app_name']=df['app_name'].apply(lambda x: id2name.get(x))
        return df
        
    def schema_table_format(self,i_str:str,err_list,schema:str,table:str):
        err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"]
        for i  in err_list:
            if i in i_str:
                i_str=i_str.replace(i,"your_schema_X.your_table_X")
        i_str=i_str.replace("your_schema_X.your_table_X", f"{schema}.{table}")
        return i_str
    # def sql_result_format(self,)
    def sql_output_format(self,sql_res,col_names):
        def print_row(a):
            return "|"+"|".join([str(item) for item in a])+"|"+"\n"
        res_str=""
        res_str+=print_row(col_names)
        for row in sql_res:
            res_str+=print_row(row)
        if res_str.endswith("\n"):
            res_str=res_str[:-1]
        
        return self.app_id_2_name(res_str)
        

    def json_decode(self,i_str:str,need_key_list):
        # exa_j['DAU_Analysis'][0]['SQL']['query']
        value_dict={}
        try:
            json_res=json.loads(i_str)
            for key_1,key_2 in need_key_list.items():
                if key_1 in json_res.keys():
                    target=key_1
                    break
            for key_2 in need_key_list[target]:
                if key_2 not in json_res[target].keys():
                    print(f"{key_2} 缺失")
                    return None
            return json_res
        except Exception as e:
            print(f"Error: {e} 解码错误有问题！")
            return None
    

# formatter=Formatter()
# print(formatter.app_id_2_name("""WHEN application_id = '2130688B018F4B44BBED68E7A42BBA1E' THEN 'Bing-Android'
# application_id = 'AE427635ADC245AE973038BCB3D7C21B' THEN 'Bing-IOS'
# application_id = '4DC5714ABCAD449BA13A9B701A3CF296' THEN 'Start-Android'
# application_id = '4A5B528B59954AAE8725B509A41FBF1A' THEN 'Start-IOS' 
# application_id = 'F185A93DE6764B098D55089F610A3FB8' THEN 'Copilot-Android'
# application_id = 'FC320C411FC12CD4DFBE9A00F3161364' THEN 'Copilot-IOS'"""))
