
import psycopg2
from psycopg2 import sql
import json
from src.Formatter import Formatter
from dotenv import load_dotenv
import os
# 全局数据库连接参数
import pandas as pd

load_dotenv()
pgsql_password=os.getenv("PGSQL_PASSWARD")
DB_CONFIG = {
    'host': 'bingviz-metrics-storage-dup.postgres.database.azure.com',
    'port': '5432',
    'dbname': 'metrics',
    'user': 'bingviz_metrics',
    'password': pgsql_password
}

class ToolPGSQL():
    def __init__(self, timeout=10,debug=True):
        print(f'init_SQL_Tool, time_out={timeout}s')
        self.DB_CONFIG = DB_CONFIG.copy()
        self.DB_CONFIG['connect_timeout'] = timeout
        self.conn = self.connect_to_postgres()
        self.debug=debug
        print(self.conn)
        if self.conn==None:
            print(DB_CONFIG)
            raise ConnectionError("Failed to connect to the database! Check your VPN connection.")
        self.cursor = self.conn.cursor()
        self.formatter = Formatter()
        
    def __del__(self) -> None:
        print('del')
        self.close_cursor_and_connection()

    def connect_to_postgres(self):
        try:
            conn = psycopg2.connect(**self.DB_CONFIG)
            print("PGSQL Connection successful")
            print(self.DB_CONFIG)
            return conn
        except Exception as e:
            print(f"Connection Error: {e}")
            raise ConnectionError("Failed to connect to the database! Check your VPN connection and PGSQL setting")
            return None

    def reconnect(self):
        """
        重新连接到数据库
        """
        self.close_cursor_and_connection()  # 关闭当前的游标和连接
        self.conn = self.connect_to_postgres()  # 重新连接到数据库
        if not self.conn:
            raise ConnectionError("Failed to reconnect to the database")
        self.cursor = self.conn.cursor()  # 创建新的游标
        print("Reconnected to the database")

    def close_cursor_and_connection(self):
        """
        关闭游标并断开连接
        """
        # print("测试",self.cursor.closed,self.cursor.closed)
        if self.conn:
            self.conn.close()  # 关闭连接
            print("Database connection closed")

    
    # def execute(self, sql_query: str, debug_sql=False) -> str:
    #     """
    #     执行SQL查询并返回结果
    #     """
    #     print("------------")
    #     print("SQL 结果", sql_query)
    #     with open("query.json", "w", encoding="utf-8") as f:
    #         json.dump({"query": sql_query}, f, ensure_ascii=False)
        
    #     try:
    #         # 执行 SQL 查询
    #         sql_res, col_names = self.fetch_complex_data(self.cursor, sql_query=sql_query)
    #     except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
    #         # 如果遇到连接错误，则重新连接并重试
    #         print(f"Database connection error: {e}")
    #         self.reconnect()
    #         sql_res, col_names = self.fetch_complex_data(self.cursor, sql_query=sql_query)
        
    #     # 提交事务
    #     if sql_res is None:
    #         return "GPT wants to take a moment to reconsider. Would you mind asking the query again?"
    #     return sql_res, col_names

    
    # def execute_query(self,cursor, query):
    #     """
    #     Executes a given SQL query using the provided cursor and returns the results.
    #     """
    #     try:
    #         print("------------")
    #         print(query)
    #         print("------------")
    #         cursor.execute(query)
    #         col_names = [desc[0] for desc in cursor.description]
    #         return cursor.fetchall(),col_names
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         return None
    # def fetch_complex_data(self, cursor, sql_query):
    #     """
    #     Fetches complex data based on the provided criteria.
    #     """
        
    #     query = sql.SQL(sql_query)
    #     # print(sql_query)
    #     results,col_names = self.execute_query(cursor, query)
    #     if results:
    #         for row in results:
    #             print("行",row)
    #         return results,col_names
    #     else:
    #         print(f"No results found for the query.")
    #         return None
    def execute_v2(self,sql_query:str,debug=True):
        """
        执行SQL查询并返回pandas结果
        """
        if self.conn:
            print("Connection closed, reconnecting...")
            self.reconnect()
        if debug:
            print("############\nSQL query:",sql_query,"\n###############")
        # with open("query.json","w",encoding="utf-8") as f:
        #     json.dump({"query":sql_query},f,ensure_ascii=False)
        df=pd.read_sql_query(sql_query,self.conn)
        return df
