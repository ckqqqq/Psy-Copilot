from src.ToolPGSQL import ToolPGSQL

"""
SELECT 
    metrics_date::date as "time", sum(CAST(metrics->'ActiveUser'->'uu'->>'uu' AS DOUBLE PRECISION)) as "DAU (R1)"
FROM sapphire.sapphire_engagement_metrics_master
WHERE $__timeFilter(metrics_date)
AND application_id IN (${Applications})
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
    GROUP BY metrics_date
    """
def dailycheck(date:str):
