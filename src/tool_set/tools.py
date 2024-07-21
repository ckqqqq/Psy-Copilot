from string import Template
from datetime import datetime, timedelta
from datetime import datetime, timedelta



key_sqls={'DAU (rolling ${rolling_day} day)': 'select metrics_date as "time", AVG("DAU") OVER (ORDER BY metrics_date ROWS BETWEEN ${rolling_day}-1 PRECEDING AND CURRENT ROW) AS "DAU (R${rolling_day})"\nfrom \n(\nSELECT \n    metrics_date, SUM(CAST(metrics->\'ActiveUser\'->\'uu\'->>\'uu\' AS DOUBLE PRECISION)) as "DAU"\nFROM sapphire.sapphire_engagement_metrics_master\nWHERE metrics_date >= to_char(cast(cast(\'$start_date\' as timestamp) + \'- ${rolling_day} DAY\' as date), \'yyyy-mm-dd\')::TEXT AND metrics_date <= \'$end_date\'\n      AND application_id IN (\'2130688B018F4B44BBED68E7A42BBA1E\',\n        \'AE427635ADC245AE973038BCB3D7C21B\',\n        \'4DC5714ABCAD449BA13A9B701A3CF296\',\n        \'4A5B528B59954AAE8725B509A41FBF1A\',\n        \'F185A93DE6764B098D55089F610A3FB8\',\n        \'FC320C411FC12CD4DFBE9A00F3161364\')\n      AND period = 1\n      AND market = \'#Overall#\'\n      AND os_version = \'#Overall#\'\n      AND device_model = \'#Overall#\'\n      AND client_version = \'#Overall#\'\n      AND client_build_type = \'#Overall#\'\n      AND install_channel_l1 = \'#Overall#\'\n      AND install_channel_l2 = \'#Overall#\'\n      AND install_channel_l3 = \'#Overall#\'\n      AND install_channel_l4 = \'#Overall#\'\n      AND mini_app = \'\'\n      AND first_launch_source = \'#Overall#\'\n      AND launch_source = \'#Overall#\'\n    GROUP BY metrics_date\n\n) t \n\n', 'User Retention 7d rolling ${rolling_day} day - all markets': 'SELECT\n    metrics_date AS "time", AVG(a."RetentionRate_7D") OVER (ORDER BY metrics_date ROWS BETWEEN ${rolling_day}-1 PRECEDING AND CURRENT ROW) AS "Retention D7 R${rolling_day}"\nFROM(\n    SELECT \n        metrics_date, sum(cast(device_retention_rate_new_daily->>\'return_count\' as DOUBLE PRECISION)) / sum(cast(device_retention_rate_new_daily->>\'dau\' as DOUBLE PRECISION)) as "RetentionRate_7D"\n    from sapphire.sapphire_retention_master\n    where metrics_date >= cast(cast(\'$start_date\' as timestamp) + \'- 7 DAY\' as TEXT) AND metrics_date <= cast(\'$end_date\' as TEXT)\n        and offset_day = 7\n        and application_id in (\'2130688B018F4B44BBED68E7A42BBA1E\',\n        \'AE427635ADC245AE973038BCB3D7C21B\',\n        \'4DC5714ABCAD449BA13A9B701A3CF296\',\n        \'4A5B528B59954AAE8725B509A41FBF1A\',\n        \'F185A93DE6764B098D55089F610A3FB8\',\n        \'FC320C411FC12CD4DFBE9A00F3161364\')\n        and market = \'#Overall#\'\n        and clientversion = \'#Overall#\'\n        and install_source in (\'Organic\', \'FirstParty\', \'RewardsUpsell\', \'PaidAds\', \'Google Ads ACI\', \'Upsell\')\n        and osversion = \'#Overall#\'\n        and build = \'#Overall#\'\n        and mini_app = \'\'\n        and launch_source = \'#Overall#\'\n        and device_model = \'#Overall#\'\n    group by metrics_date\n) a', 'Chat Active DAU (rolling ${rolling_day} day)': 'select  metrics_date as "time", AVG("Chat_Active_DAU") OVER (ORDER BY metrics_date ROWS BETWEEN ${rolling_day}-1 PRECEDING AND CURRENT ROW) AS "Chat Active DAU (R${rolling_day})"\nfrom (\nSELECT \n  metrics_date,\n  SUM(CAST(metrics->\'ActiveUser\'->\'dau\'->\'chat_active_dau\' AS DOUBLE PRECISION)) AS "Chat_Active_DAU"\nFROM codex_metrics.codex_engagement_metrics_master\nWHERE metrics_date >= to_char(cast(cast(\'$start_date\' as timestamp) + \'- ${rolling_day} DAY\' as date), \'yyyy-mm-dd\')::TEXT \n  AND metrics_date <= \'$end_date\'\n  AND application_id in (\'2130688B018F4B44BBED68E7A42BBA1E\',\n        \'AE427635ADC245AE973038BCB3D7C21B\',\n        \'4DC5714ABCAD449BA13A9B701A3CF296\',\n        \'4A5B528B59954AAE8725B509A41FBF1A\',\n        \'F185A93DE6764B098D55089F610A3FB8\',\n        \'FC320C411FC12CD4DFBE9A00F3161364\')\n\tAND id_type= \'reportable_id\'\n  AND market =\'#Overall#\'\n  AND install_channel_l1 =\'#Overall#\'\n  AND install_channel_l2 =\'#Overall#\'\n\tAND first_launch_entry_point =\'#Overall#\'\n\tAND period = 1\n\tAND os_version =\'#Overall#\'\n\tAND device_model =\'#Overall#\'\n\tAND client_version =\'#Overall#\'\n\tAND client_build_type =\'#Overall#\'\n\tAND install_channel_l3 =\'#Overall#\'\n\tAND install_channel_l4 =\'#Overall#\'\n\tAND mini_app =\'#Overall#\'\n\tAND first_launch_source =\'#Overall#\'\nGROUP BY metrics_date\n) t\n'}

from src.ToolPGSQL import ToolPGSQL
toolPGSQL=ToolPGSQL(10)
def tool_dau(start_date:str,end_date:str,rolling_day=1):
    """
    {
        "name": "tool_dau",
        "description": "Retrieve DAU within the [start_date, end_date] time range, optionally using a rolling average over rolling_day days.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "start_date e.g., '2024-07-10'"
                },
                "end_date": {
                    "type": "string",
                    "description": "end_date e.g., '2024-07-15'"
                },
                "rolling_day": {
                    "type": "string",
                    "description": "rolling average day (e.g., 7 or 1)"
                }
            }
        }
    }

    """
    sql_template=key_sqls["DAU (rolling ${rolling_day} day)"]
    return_pandas=toolPGSQL.execute_v2(Template(sql_template).substitute(start_date=start_date,end_date=end_date,rolling_day=rolling_day),debug=False)
    return return_pandas
def tool_retention(start_date:str,end_date:str,rolling_day=7):
    """
    {
        "name": "tool_retention",
        "description": "Retrieve User Retention within the [start_date, end_date] time range, optionally using a rolling average over rolling_day days.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "start_date e.g., '2024-07-10'"
                },
                "end_date": {
                    "type": "string",
                    "description": "end_date e.g., '2024-07-15'"
                },
                "rolling_day": {
                    "type": "string",
                    "description": "rolling average day (e.g., 7 or 1)"
                }
            }
        }
    }
    """
    sql_template=key_sqls['User Retention 7d rolling ${rolling_day} day - all markets']
    return_pandas=toolPGSQL.execute_v2(Template(sql_template).substitute(start_date=start_date,end_date=end_date,dau_metrics_date=end_date,rolling_day=rolling_day),debug=False)
    return return_pandas
    
def tool_chat_dau(start_date:str,end_date:str,rolling_day=1):
    """
    {
        "name": "tool_chat_dau",
        "description": "Retrieve Chat Active DAU within the [start_date, end_date] time range, optionally using a rolling average over rolling_day days.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "start_date e.g., '2024-07-10'"
                },
                "end_date": {
                    "type": "string",
                    "description": "end_date e.g., '2024-07-15'"
                },
                "rolling_day": {
                    "type": "string",
                    "description": "rolling average day (e.g., 7 or 1)"
                }
            }
        }
    }
    """
    sql_template=key_sqls["Chat Active DAU (rolling ${rolling_day} day)"]
    return_pandas=toolPGSQL.execute_v2(Template(sql_template).substitute(start_date=start_date,end_date=end_date,dau_metrics_date=end_date,rolling_day=rolling_day),debug=False)
    return return_pandas
check_date="2024-07-11"
def tool_daily_check(check_date:str="2024-07-11"):
    """
    {
        "name": "tool_daily_check",
        "description": "Retrieve daily check results for [check_date], providing metrics for DAU, retention, and Chat DAU.",
        "parameters": {
            "type": "object",
            "properties": {
                "check_date": {
                    "type": "string",
                    "description": "Date for which daily metrics are retrieved (e.g., '2024-07-11')."
                }
            }
        },
        "output": {
            "type": "string",
            "description": "A formatted string containing the daily check results."
        }
    }
    """
    # last date having data

    res_list=[]
    tool_functions= [tool_dau,tool_retention,tool_chat_dau]
    for tool in tool_functions:
        metrics_date=tool(start_date=(datetime.strptime(check_date, '%Y-%m-%d') -  timedelta(days=7)).strftime('%Y-%m-%d'),end_date=check_date,rolling_day=1).iloc[-1].loc["time"]
        seven_days_ago=(datetime.strptime(metrics_date, '%Y-%m-%d') -  timedelta(days=7)).strftime('%Y-%m-%d')
        print(metrics_date,seven_days_ago)
        data_r1=tool(start_date=seven_days_ago,end_date=metrics_date,rolling_day=1)
        r1_wow_change=data_r1.loc[data_r1['time']==metrics_date].iloc[-1,-1]-data_r1.loc[data_r1['time']==seven_days_ago].iloc[-1,-1]

        data_r7=tool(start_date=seven_days_ago,end_date=metrics_date,rolling_day=7)
        r7_wow_change=data_r7.loc[data_r7['time']==metrics_date].iloc[-1,-1]-data_r7.loc[data_r7['time']==seven_days_ago].iloc[-1,-1]
        res_list.append([metrics_date,data_r7.iloc[-1,-1],r7_wow_change,data_r1.iloc[-1,-1],r1_wow_change])

    
    # print(res_list)
    daily_template=f"""Daily Check \n Check Date: {check_date}""";
    
    daily_template+=f"""\n Metrics Date: {res_list[0][0]} DAU: avg-7d {res_list[0][1]/1000000:.3f} M ({res_list[0][2]/1000:.3f}k WoW), last-1d {res_list[0][3]/1000000:.3f} M ({res_list[0][4]/1000:.3f}k WoW)"""
    daily_template+=f"""\n Metrics Date: {res_list[1][0]} New Retention Day7: avg-7d {res_list[1][1]*100:.1f}% ({res_list[1][2]*100:.2f} pp WoW), last-1d {res_list[1][3]*100:.3f}% ({res_list[1][4]*100:.2f}pp WoW)"""
    daily_template+=f"""\n Metrics Date: {res_list[2][0]} Chat DAU: avg-7d {res_list[2][1]/1000000:.3f} M ({res_list[2][2]/1000:.3f}k WoW), last-1d {res_list[2][3]/1000000:.3f} M ({res_list[2][4]/1000:.3f} K WoW) \n"""
    daily_template+="""| **Check Item**         | **Link/Status**                                                                                       |\n| ---------------------- | ----------------------------------------------------------------------------------------------------- |\n| **OKR - SA DAU**       | [DAU ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229619)       |\n| **OKR - SA Retention** | [Retention ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229646) |\n| **OKR - Codex Chat**   | [Codex ASO](https://msasg.visualstudio.com/SAN%20SA/_backlogs/backlog/SA%20Leadership%20Team/Epics?workitem=6229592)     |\n
    """
    return daily_template
# DAU: avg-7d 5.13 M (-193.0k WoW), last-1d 5.21 M (-46.2k WoW)
# New Retention Day7: avg-7d 10.54% (+2.66pp WoW), last-1d 12.29% (+4.23pp WoW)
# Chat DAU: avg-7d 1.13 M (-64.7k WoW), last-1d 1.14 M (-74.5 K WoW)"""
tools_list=[tool_dau,tool_retention,tool_chat_dau,tool_daily_check]