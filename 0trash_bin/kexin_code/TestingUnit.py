import argparse
from ToolPGSQL import ToolPGSQL
from Formatter import Formatter
# 定义函数
formatter=Formatter()
sql_querys=[
    """SELECT market,
SUM( CAST( metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION ) ) AS dau 
FROM 
your_schema.your_table 
WHERE metrics_date BETWEEN  '2024-06-09' AND '2024-06-09'
AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')
GROUP BY market
ORDER BY dau DESC
LIMIT 10;"""
]
def test_A():
    print("Running test A")
    toolPGSQL=ToolPGSQL()
    sql_query=formatter.schema_table_format(sql_querys[0],err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"], schema='sapphire',table='sapphire_engagement_metrics_master')
    result=toolPGSQL.execute(sql_query)
    

def test_B():
    print("test sql_formatter")
    formatter=Formatter()
    sql_output=formatter.sql_output_format([('#Overall#', 705696946.0), ('en-xl', 35851980.0), ('en-us', 27332840.0), ('es-xl', 24975081.0), ('en-in', 22389759.0), ('pt-br', 15275964.0), ('zh-cn', 11140802.0), ('es-mx', 8449721.0), ('ja-jp', 8026148.0), ('de-de', 7703039.0)], ['market', 'dau'])
    print(sql_output)
def test_C():
    print("Running test C")

def test_D():
    print("Running test D")

def test_reconnect():
    toolPGSQL=ToolPGSQL(timeout=15)
    toolPGSQL.close_cursor_and_connection()
    sql_res_df = toolPGSQL.execute_query_with_pandas("""SELECT 
        metrics_date, 
        SUM( CAST( metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION ) ) AS dau 
        FROM 
        sapphire.sapphire_engagement_metrics_master 
        WHERE metrics_date = '2024-06-25' AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')
        AND period = 1    
        AND os_version = '#Overall#'     
        AND device_model = '#Overall#'    
        AND client_version = '#Overall#' 
        AND client_build_type = '#Overall#'    
        AND install_channel_l1 = '#Overall#'    
        AND install_channel_l2 = '#Overall#'    
        AND install_channel_l3 = '#Overall#'    
        AND install_channel_l4 = '#Overall#' 
        AND mini_app = '' 
        AND first_launch_source = '#Overall#'    
        AND launch_source = '#Overall#' 
        AND market = '#Overall#'     
        GROUP BY metrics_date
        LIMIT 1;""")
    
    print("PGSQL run completed")
    print(sql_res_df)


# 将函数存储在字典中，以便根据名称调用
tests = {
    'A': test_A,
    'B': test_B,
    'C': test_C,
    'D': test_D,
    'E': test_reconnect
}

# 主程序
def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="Run specific test by name")
    # 添加参数
    parser.add_argument('--func', type=str, help="Name of the test to run")

    # 解析命令行参数
    args = parser.parse_args()

    # 根据传入的函数名调用相应的函数
    if args.func in tests:
        tests[args.func]()
    else:
        print("Invalid test name")

if __name__ == '__main__':
    main()























































    """
    import argparse

# 定义函数
def test_A():
    print("Running test A")

def test_B():
    print("Running test B")

def test_C():
    print("Running test C")

def test_D():
    print("Running test D")

# 将函数存储在字典中，以便根据名称调用
tests = {
    'A': test_A,
    'B': test_B,
    'C': test_C,
    'D': test_D
}

# 主程序
def main():
    # 创建解析器
    parser = argparse.ArgumentParser(description="Run specific test by name")
    # 添加参数
    parser.add_argument('test_name', type=str, help="Name of the test to run")

    # 解析命令行参数
    args = parser.parse_args()

    # 根据传入的函数名调用相应的函数
    if args.test_name in tests:
        tests[args.test_name]()
    else:
        print("Invalid test name")

if __name__ == '__main__':
    main()
    """