# css to inject related to info bar
from code_editor import code_editor
import streamlit as st


test_code="""select metrics_date::date AS "time", dau as "DAU", b.mini_app_name
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
defaut_btn_setting=[
 {
   "name": "Copy",
   "feather": "Copy",
   "hasText": True,
   "alwaysOn": True,
   "commands": ["copyAll"],
   "style": {"top": "0.46rem", "right": "0.4rem"}
 },
 {
   "name": "Shortcuts",
   "feather": "Type",
   "class": "shortcuts-button",
   "hasText": True,
   "commands": ["toggleKeyboardShortcuts"],
   "style": {"bottom": "calc(50% + 1.75rem)", "right": "0.4rem"}
 },
 {
   "name": "Collapse",
   "feather": "Minimize2",
   "hasText": True,
   "commands": ["selectall",
                "toggleSplitSelectionIntoLines",
                "gotolinestart",
                "gotolinestart",
                "backspace"],
   "style": {"bottom": "calc(50% - 1.25rem)", "right": "0.4rem"}
 },
 {
   "name": "Save",
   "feather": "Save",
   "hasText": True,
   "commands": ["save-state", ["response","saved"]],
   "response": "saved",
   "style": {"bottom": "calc(50% - 4.25rem)", "right": "0.4rem"}
 },
 {
   "name": "Run",
   "feather": "Play",
   "primary": True,
   "hasText": True,
   "showWithIcon": True,
   "commands": ["submit"],
   "style": {"bottom": "0.44rem", "right": "0.4rem"}
 },
 {
   "name": "Command",
   "feather": "Terminal",
   "primary": True,
   "hasText": True,
   "commands": ["openCommandPallete"],
   "style": {"bottom": "3.5rem", "right": "0.4rem"}
 }
]
# code_editor_response = code_editor(
#         code=test_code,
#         buttons=defaut_btn_setting,
#         theme="dark",
#         lang="pgsql",
#     )
# # code_handle_action(code_editor_response)

