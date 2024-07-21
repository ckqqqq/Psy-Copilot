
import psycopg2
from psycopg2 import sql
import json
from Formatter import Formatter
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
    def __init__(self, timeout=10):
        """
        Initialize ToolPGSQL class and set up database connection and cursor
        """
        print(f'init_SQL_Tool, time_out={timeout}s')
        self.DB_CONFIG = DB_CONFIG.copy()
        self.DB_CONFIG['connect_timeout'] = timeout
        self.conn = self.connect_to_postgres()  # Connect to the database
        if not self.conn:
            raise ConnectionError("Failed to connect to the database")
        self.cursor = self.conn.cursor()  # Create a cursor
        
        self.formatter = Formatter()
        
    def __del__(self) -> None:
        """
        Destructor, closes the cursor and connection
        """
        print('del')
        self.close_cursor_and_connection()

    def execute(self, sql_query: str, debug_sql=False) -> str:
        """
        Execute SQL query and return the result
        """
        print("------------")
        print("SQL result", sql_query)
        with open("query.json", "w", encoding="utf-8") as f:
            json.dump({"query": sql_query}, f, ensure_ascii=False)
        
        try:
            # Execute the SQL query
            sql_res, col_names = self.fetch_complex_data(self.cursor, sql_query=sql_query)
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
            # If a connection error occurs, reconnect and retry
            print(f"Database connection error: {e}")
            self.reconnect()
            sql_res, col_names = self.fetch_complex_data(self.cursor, sql_query=sql_query)
        
        # Commit the transaction
        if sql_res is None:
            return "GPT wants to take a moment to reconsider. Would you mind asking the query again?"
        return sql_res, col_names

    def connect_to_postgres(self):
        """
        Connect to the PostgreSQL database
        """
        try:
            conn = psycopg2.connect(**self.DB_CONFIG)
            print("PGSQL Connection successful")
            print(self.DB_CONFIG)
            return conn
        except Exception as e:
            print(f"Error: {e}")
            return None

    def reconnect(self):
        """
        Reconnect to the database
        """
        self.close_cursor_and_connection()  # Close the current cursor and connection
        self.conn = self.connect_to_postgres()  # Reconnect to the database
        if not self.conn:
            raise ConnectionError("Failed to reconnect to the database")
        self.cursor = self.conn.cursor()  # Create a new cursor
        print("Reconnected to the database")

    def close_cursor_and_connection(self):
        """
        Close the cursor and disconnect
        """
        if self.cursor:
            self.cursor.close()  # Close the cursor
        if self.conn:
            self.conn.close()  # Close the connection
            print("Database connection closed")

    def fetch_complex_data(self, cursor, sql_query):
        """
        Fetches complex data based on the provided criteria.
        """
        query = sql.SQL(sql_query)
        results, col_names = self.execute_query(cursor, query)
        if results:
            for row in results:
                print("行", row)
            return results, col_names
        else:
            print(f"No results found for the query.")
            return None

    def execute_query_with_pandas(self, sql_query: str):
        """
        Execute SQL query and return the result as a DataFrame
        """
        print("SQL result saved locally", sql_query)
        with open("query.json", "w", encoding="utf-8") as f:
            json.dump({"query": sql_query}, f, ensure_ascii=False)
        
        # Check if the connection is closed and reconnect if necessary
        if self.conn.closed:
            print("Connection is closed. Reconnecting...")
            self.reconnect()

        try:
            # Execute the SQL query and fetch the result into a DataFrame
            df = pd.read_sql_query(sql_query, self.conn)
        except (psycopg2.InterfaceError, psycopg2.OperationalError) as e:
            # If a connection error occurs, reconnect and retry
            print(f"Database connection error: {e}")
            self.reconnect()
            df = pd.read_sql_query(sql_query, self.conn)
        
        print(df.head(10))
        return df

    

toolPGSQL=ToolPGSQL(timeout=15)
toolPGSQL.close_cursor_and_connection()
toolPGSQL.execute_query_with_pandas("""SELECT 
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
