import argparse
from src.ToolPGSQL import ToolPGSQL
from src.Formatter import Formatter
import datetime
from src.AgentToolUser import AgentToolUser

testPGSQL={
    
}


current_time=datetime.datetime.now()
delta=datetime.timedelta(days=30)
previous_time=current_time-delta


formatter=Formatter()
raw_pgsql="""-- SELECT\r\n--     metrics_date::date AS \"time\", AVG(a.\"RetentionRate_1D\") OVER (ORDER BY metrics_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS \"Organic\"\r\n-- FROM(\r\n    SELECT \r\n        metrics_date::date AS \"time\", sum(cast(device_retention_rate_new_daily->>'return_count' as DOUBLE PRECISION)) / sum(cast(device_retention_rate_new_daily->>'dau' as DOUBLE PRECISION)) as \"Organic\"\r\n    from sapphire.sapphire_retention_master\r\n    where metrics_date >= cast(cast(${__from:date:'YYYY-MM-DD'} as timestamp) + '- 7 DAY' as TEXT) AND metrics_date <= cast(${__to:date:'YYYY-MM-DD'} as TEXT)\r\n        and offset_day = 14\r\n        and application_id in (${Applications})\r\n        and market = '#Overall#'\r\n        and clientversion = '#Overall#'\r\n        and install_source in ('Organic')\r\n        and osversion = '#Overall#'\r\n        and build = '#Overall#'\r\n        and mini_app = ''\r\n        and launch_source = '#Overall#'\r\n        and device_model = '#Overall#'\r\n    group by metrics_date\r\n    ORDER BY metrics_date\r\n-- ) a;"""
raw_pgsql=raw_pgsql.replace("${__from:date:'YYYY-MM-DD'}",str(previous_time))
raw_pgsql=raw_pgsql.replace("${__to:date:'YYYY-MM-DD'}",str(current_time))
raw_pgsql=raw_pgsql.replace(r"${Applications}",",".join('2130688B018F4B44BBED68E7A42BBA1E'))

sql_querys=[
    raw_pgsql
]
def test_A():
    print("Running test A")
    toolPGSQL=ToolPGSQL()
    sql_query=formatter.schema_table_format(sql_querys[0],err_list=["table_name",'your_table_name',r"{}.{}","your_schema.your_table"], schema='sapphire',table='sapphire_engagement_metrics_master')
    result=toolPGSQL.execute_v2(sql_query)
    

def test_B():
    print("test sql_formatter")
    formatter=Formatter()
    sql_output=formatter.sql_output_format([('#Overall#', 705696946.0), ('en-xl', 35851980.0), ('en-us', 27332840.0), ('es-xl', 24975081.0), ('en-in', 22389759.0), ('pt-br', 15275964.0), ('zh-cn', 11140802.0), ('es-mx', 8449721.0), ('ja-jp', 8026148.0), ('de-de', 7703039.0)], ['market', 'dau'])
    print(sql_output)
def test_C():

    toolPGSQL=ToolPGSQL(timeout=15)
    print("测试链接")
    pandas_res=toolPGSQL.execute_v2(testPGSQL["DAU (R7)"])
    print(pandas_res)
    print("Running test C")

def test_D():
    print("Running test D")
    agentToolUser=AgentToolUser()
    print(agentToolUser.use_tool("请给我2024年7月14日daily_check的结果。"))
    # print(agentToolUser.runTool("tool_daily_check(check_date='2024-07-11')"))

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