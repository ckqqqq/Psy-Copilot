from string import Template
import pandas as pd
# pd.set_option('display.max_colwidth', None)
from azure.identity import AzureCliCredential, DefaultAzureCredential
from openai import AzureOpenAI
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import json


import datetime

# Define a constant for the number of days to go back
DAYS_BACK = 1

# Get today's date
today = datetime.date.today()

# Calculate and get the date for the previous day
default_day = today - datetime.timedelta(days=DAYS_BACK)

# Print the default date
print("Default date:", default_day)

miniapp_top_10_dau_query=""" SELECT 
metrics_date::date AS "time", dau as "DAU", b.mini_app_name
from (
SELECT 
metrics_date, mini_app, sum(dau) as dau
FROM sapphire.sapphire_mini_apps_dau_master
WHERE metrics_date = '2024-06-07'
AND market = '#Overall#'
AND first_launch_source = '#Overall#'
AND client_version = '#Overall#'
AND install_source = '#Overall#'
AND os_version = '#Overall#'
AND client_build_type = '#Overall#'
AND application_package = '#Overall#'
group by metrics_date, mini_app
) as a 
inner join (
SELECT mini_app_id, mini_app_name 
FROM sapphire.sapphire_mini_apps 
where is_in_appstarter='true' and is_in_prod = 'true' and date = '2024-06-07'
GROUP BY mini_app_id, mini_app_name
) as b
on lower(a.mini_app) = lower(b.mini_app_id)
order by metrics_date, dau desc
LIMIT 10;"""

def init_prompt_dau():
    print("init_prompt_dau")

    #  system_prompt
    """

    # Step 2: 导入所需模块
    from azure.identity import AzureCliCredential, DefaultAzureCredential
    from openai import AzureOpenAI

    # Step 3: 获取 Azure CLI 凭据
    credential = AzureCliCredential()

    """
    # export PATH=$PATH:/home/jason00

    dau_analysis_sql_query=""" SELECT 
    metrics_date, 
    application_id, 
    SUM( CAST( metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION ) ) AS dau 
    FROM 
    your_schema.your_table 
    WHERE metrics_date BETWEEN '2024-06-09' AND '2024-06-09' AND period = 1    
    AND os_version = '#Overall#'     
    AND device_model = '#Overall#'    
    AND client_version = '#Overall#' 
    AND client_build_type = '#Overall#'    
    AND install_channel_l1 = '#Overall#'    
    AND install_channel_l2 = '#Overall#'    
    AND install_channel_l3 = '#Overall#'    
    AND install_channel_l4 = '#Overall#' 
    AND first_launch_source = '#Overall#'    
    AND launch_source = '#Overall#' 
    AND market = '#Overall#'     
    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B') 
    GROUP BY metrics_date, application_id
    LIMIT 10;""" 
    wau_analysis_sql_query=""" SELECT 
    metrics_date, 
    application_id, 
    SUM( CAST( metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION ) ) AS dau 
    FROM 
    your_schema.your_table 
    WHERE metrics_date BETWEEN '2024-06-09' AND '2024-06-09' AND period = 7    
    AND os_version = '#Overall#'     
    AND device_model = '#Overall#'    
    AND client_version = '#Overall#' 
    AND client_build_type = '#Overall#'    
    AND install_channel_l1 = '#Overall#'    
    AND install_channel_l2 = '#Overall#'    
    AND install_channel_l3 = '#Overall#'    
    AND install_channel_l4 = '#Overall#'
    AND first_launch_source = '#Overall#'    
    AND launch_source = '#Overall#' 
    AND market = '#Overall#'     
    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B') 
    GROUP BY metrics_date, application_id
    LIMIT 10;"""
    market_top_10_dau_query="""
    SELECT market,
    SUM( CAST( metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION ) ) AS dau 
    FROM 
    your_schema.your_table 
    WHERE metrics_date BETWEEN  '2024-06-09' AND '2024-06-09'
    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')
    GROUP BY market
    ORDER BY dau DESC
    LIMIT 10;"""
    market_count_dau_query="""
    SELECT count( distinct( market ) )
    FROM 
    your_schema.your_table 
    WHERE metrics_date BETWEEN  '2024-06-09' AND '2024-06-09'
    AND application_id IN ('2130688B018F4B44BBED68E7A42BBA1E', 'AE427635ADC245AE973038BCB3D7C21B')
    LIMIT 10;
    """
    ar_query="""
    SELECT 
    market,
    COUNT(*) AS argentinian_record_count
    FROM
    sapphire.sapphire_engagement_metrics_master
    WHERE metrics_date = '2024-06-09'
    AND market = 'es-ar'
    GROUP BY market
    LIMIT 10;"""

    json_fewshot=[
    {
        "Analysis": {
            "input":"Bing APP 一天有多少用户？",
            "reasoning":"The objective is to retrieve the Number of Daily Active Users (DAU) for both Bing-Android and Bing-IOS applications on a specific date, June 9th, 2024. We will sum the user counts from the 'ActiveUser'->'uu' metrics JSON field and filter for the specific day across both application IDs.",
            "SQL": dau_analysis_sql_query,
            "date": ["2024-06-09","2024-06-09"],
        },
    },
      {
        "Analysis": {
            "input":"Bing APP一周有多少用户？",
            "reasoning":"获取在2024年6月3日至6月9日这一周，指定的两个应用程序（Bing-Android和Bing-IOS）的日活跃用户数（DAU）",
            "SQL": wau_analysis_sql_query,
            "date": ["2024-06-09","2024-06-09"],
        },
      },
    {
        "Analysis": {
            "input":"告诉我Bing APP用户最多的一个前十个市场",
            "reasoning":"获取在2024年6月9日这一天，指定的两个应用程序（Bing-Android和Bing-IOS）的日活跃用户数（DAU）,先对其进行降序排序，然后选取前10个dau最大的项。",
            "SQL": market_top_10_dau_query,
            "date": ["2024-06-09","2024-06-09"],
        },
    },
    {
        "Analysis": {
            "input":"我们有阿根廷市场吗？",
            "reasoning":"In this request, we are checking for the presence of Argentinian market, identified by the 'es-ar' market code, across all applications in the dataset. We will use the default date, June 9th, 2024, and count for any record with 'es-ar' in the market field.",
            "SQL": ar_query,
            "date": ["2024-06-09","2024-06-09"],
        },
    },
    ]

    # template = Template("我的名字是 $name，我今年 $age 岁。")
    metrics=r"""{'ActiveUser': {'uu': {'uu': 467.0}, 'msa': {'msa_uu': 0.0}, 'msb': {'msb_uu': 0.0}, 'session': {'session_cnt': 894.0}, 'dwelltime': {'dwelltime': 107686.0, 'dwelltime_uu': 382.0}}"""
    # metrics=r"""test"""
    # .format(metrics=metrics,default_day=default_day)
    prompt_dau = Template("""
    Context: 
    Now we have the user data for some apps, these app are search apps, it intagrated the copilot for AI.
    User can also search for information, this app get revenue by ads, and it also have many miniapps for different feature.
    We did some AB test based on user interaction data from an app, 
    which includes various metrics such as user behavior, codex (AI) behavior, and search behavior. 

    The data for each user is structured as a sentence.

    The goal is to generate SQL and more information.
    The query should focus on：
    market:
    Format is "en-us",first two is language, last two is country (xl means other counrty that we can not get info.)
    Eg."en-us" means American people speak English.

    application_id: user will describe a app name, and you need to use id when you serach.
    WHEN application_id = '2130688B018F4B44BBED68E7A42BBA1E' THEN 'Bing-Android'
    application_id = 'AE427635ADC245AE973038BCB3D7C21B' THEN 'Bing-IOS'
    application_id = '4DC5714ABCAD449BA13A9B701A3CF296' THEN 'Start-Android'
    application_id = '4A5B528B59954AAE8725B509A41FBF1A' THEN 'Start-IOS' 
    application_id = 'F185A93DE6764B098D55089F610A3FB8' THEN 'Copilot-Android'
    application_id = 'FC320C411FC12CD4DFBE9A00F3161364' THEN 'Copilot-IOS'

    If user did not give you os name, you need to Get Both of them.
    Eg."Bing"means ['2130688B018F4B44BBED68E7A42BBA1E','AE427635ADC245AE973038BCB3D7C21B']

    metrics_date： if not set in the content, it is $default_day in the format "YYYY-MM-DD".
    - Always use the exact date in the SQL query, do not use relative date expressions like `current_date - INTERVAL '1 day'`.
                          
    period: 
    user period = 1 and metrics_date=YYYY-MM-DD means daily active users (dau) for that specific day, 
    user period = 7 and metrics_date=YYYY-MM-DD means weekly active users (wau) calculated for that specific day, 
    user period = 30 and metrics_date=YYYY-MM-DD means monthly active users (mau) calculated for that specific day.
    Generate the SQL query based on the following conditions:
    - When querying DAU, generate "WHERE metrics_date = 'YYYY-MM-DD' AND period = 1".
    - When querying WAU, generate "WHERE metrics_date = 'YYYY-MM-DD' AND period = 7".
    - When querying MAU, generate "WHERE metrics_date = 'YYYY-MM-DD' AND period = 30".
                          
                          
    Data Definition:
        If you need to get all data in this type, use "#Overall#". eg. market="#Overall", remember to take in every query if no specific.
        Otherwise, if you need to specify type, use your type. eg. market="en-us".Not only in "market", use it in all type.
        Here is the schema of dau table (sapphire.sapphire_engagement_metrics_master):                                                                                                                                                                                                                                                                
            umid                 | 1736681
            metrics_date         | 2022-09-23
            application_id       | 4DC5714ABCAD449BA13A9B701A3CF296
            market               | en-in
            os_version           | #Overall#
            device_model         | #Overall#
            client_version       | 23.3.400914606
            client_build_type    | #Overall#
            install_channel_l1   | #Overall#
            install_channel_l2   | #Overall#
            install_channel_l3   | #Overall#
            install_channel_l4   | #Overall#
            mini_app             | ''
            first_launch_source  | #Overall#
            launch_source        | #Overall#
            metrics              | $metrics
                          
    Default value (remember to take in every query if no specific):
        AND period = 1
        AND market = '#Overall#'
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

    Output Format: 
        Each set of data returns one json, followed by an example based on the provided data.


        Specifications:
        - Analyze the input and describe their demand.
        - Use these column to identify and describe user demand.
        - Provide a detailed and correct pgsql query for each input.
        - Limit the output length to avoid excessive verbosity.
        - Refer the schema of table. Include the default conditions in every query to ensure accurate calculation by considering all categories
        - To calculate user count, always use `sum(dau) as dau`
        - Do not use `#Overall#` for `application_id`. It should always be a specific ID or a list of IDs.

    Task Examples: 

    """).substitute(metrics=metrics,default_day=default_day)


    # json_fewshot_str=json.dumps(json_fewshot,ensure_ascii=False)
    for idx,shot in enumerate(json_fewshot):
        prompt_dau+="Input"+str(idx)+":\n"+shot["Analysis"]["input"]+"\n"
        prompt_dau+="Output"+str(idx)+":\n"+json.dumps(shot,ensure_ascii=False)+"\n"
    return prompt_dau
# prompt_dau=init_prompt()



def init_prompt_miniapp():
    
    prompt_miniapp=Template("""
    Context: 
    Now we have the user data for some apps, these app are search apps, it intagrated the copilot for AI.
    User can also search for information, this app get revenue by ads, and it also have many miniapps for different feature.
    We did some AB test based on user interaction data from an app, 
    which includes various metrics such as user behavior, codex (AI) behavior, and search behavior. 

    The data for each user is structured as a sentence.

    The goal is to generate SQL and more information.
    The query should focus on：
    market:
    Format is "en-us",first two is language, last two is country (xl means other counrty that we can not get info.)
    Eg."en-us" means American people speak English.

    application_id: user will describe a app name, and you need to use id when you serach.
    WHEN application_id = '2130688B018F4B44BBED68E7A42BBA1E' THEN 'Bing-Android'
    application_id = 'AE427635ADC245AE973038BCB3D7C21B' THEN 'Bing-IOS'
    application_id = '4DC5714ABCAD449BA13A9B701A3CF296' THEN 'Start-Android'
    application_id = '4A5B528B59954AAE8725B509A41FBF1A' THEN 'Start-IOS' 
    application_id = 'F185A93DE6764B098D55089F610A3FB8' THEN 'Copilot-Android'
    application_id = 'FC320C411FC12CD4DFBE9A00F3161364' THEN 'Copilot-IOS'

    If user did not give you os name, you need to Get Both of them.
    Eg."Bing"means ['2130688B018F4B44BBED68E7A42BBA1E','AE427635ADC245AE973038BCB3D7C21B']

    metrics_date： if not set in the content, it is $default_day in the format "YYYY-MM-DD".
    - Always use the exact date in the SQL query, do not use relative date expressions like `current_date - INTERVAL '1 day'`.

    date: Must add date query and only contain 1 day when you search in the sapphire.sapphire_mini_apps. Otherwise you will get repeat data which generate wrong answer.
             
    For `mini_app`：
    - mini_app in sapphire.sapphire_mini_apps_dau_master == mini_app_id in sapphire.sapphire_mini_apps.
    - Use subqueries to isolate data and avoid repeated rows.
    - First, aggregate data from `sapphire.sapphire_mini_apps_dau_master`.
    - Then, join the aggregated data with `sapphire.sapphire_mini_apps` on the `mini_app_id` field, ensuring to filter by the correct date `metrics_date` in the subquery..

    there are some miniapp example in the database:
        ('HomePageFeed',)
        ('Rewards',)
        ('Weather',)
        ('NC-Settings',)
        ('Scaffolding: Settings (NativeComponent)',)
        ('Wallpapers',)
        ('Designer (Image Creator)',)
        ('Image Creator',)
        ('Bing Image Creator',)
        ('Cash Back',)
        ('Shopping: Cash Back',)

    Data Definition:
        If you need to get all data in this type, use "#Overall#". eg. market="#Overall", remember to take in every query if no specific.
        Otherwise, if you need to specify type, use your type. eg. market="en-us".Not only in "market", use it in all type.
             
        Here is the schema of miniapp's dau table (sapphire.sapphire_mini_apps_dau_master):                                                                                                                                                                                                                                                                
            metrics_date         | 2022-01-01
            application_id       | AE427635ADC245AE973038BCB3D7C21B
            mini_app             | C58CEA7EF6E89CA39F9401EDB12D241D
            market               | #Overall#
            first_launch_source  | #Overall#
            client_version       | #Overall#
            install_source       | #Overall#
            os_version           | #Overall#
            client_build_type    | #Overall#
            dau                  | 20
            create_at            | 2022-07-19 11:24:15.454516+00:00
            updated_at           | 2022-07-19 11:24:15.454516+00:00
            application_package  | #Overall#
        Default value (remember to take in every query if no specific):
            AND market = '#Overall#'
            AND first_launch_source = '#Overall#'
            AND client_version = '#Overall#'
            AND install_source = '#Overall#'
            AND os_version = '#Overall#'
            AND client_build_type = '#Overall#'
            AND application_package = '#Overall#'
                
        Here is the schema of miniapp table (sapphire.sapphire_mini_apps):
            umid                 | 61
            mini_app_id          | C58CEA7EF6E89CA39F9401EDB12D241D
            mini_app_name        | Weather
            mini_app_category    | Productivity
            is_in_appstarter     | True
            is_in_prod           | True
            platform_list        | Android,iOS
            build_type_list      | daily,dev,dogfood,production
            date                 | 2021-09-16


    Output Format: 
        Each set of data returns one json, followed by an example based on the provided data.

        result_count: How many result will get after query, for example, if group by 2 date and 3 application, it will get 2*3=6 columns.
        if you guess the column will more than 100, eg. group by market, please use 100.

        Specifications:
        - Analyze the input and describe their demand.
        - Use these column to identify and describe user demand.
        - Provide a detailed and correct pgsql query for each input.
        - Limit the output length to avoid excessive verbosity.
        - Refer the schema of table. Include the default conditions in every query to ensure accurate calculation by considering all categories
        - To calculate user count, always use `sum(dau) as dau`
        - Do not use `#Overall#` for `application_id`. It should always be a specific ID or a list of IDs.

    Task Examples: 

    """).substitute(default_day=default_day)

    json_fewshot=[

    {
        "Analysis": {
                "input":"dau排名前十的miniapp有哪些？",
                "reasoning":"获取在2024年6月7日这一天，日活跃用户数（dau）排名前十的miniapp",
                "SQL": miniapp_top_10_dau_query,
                "date": ["2024-06-07","2024-06-07"],
        },
    },
    ]
    for idx,shot in enumerate(json_fewshot):
        prompt_miniapp+="Input"+str(idx)+"\n"+shot["Analysis"]["input"]+":\n"
        prompt_miniapp+="Output"+str(idx)+"\n"+json.dumps(shot,ensure_ascii=False)+":\n"
        
    return prompt_miniapp