from app.config import config
import requests
from datetime import datetime, timedelta

async def find_constrain_data(acn:str, acc: str, acg: str, acs: str):
    """Find data"""
    return build_query(acn=acn, acc=acc, line='a')


async def build_query(acn: str, acc: str, line: str):
    """Build Query for site metrics"""
    end_date = datetime.now()
    start_date = end_date - timedelta(minutes=5)
    start_seconds = round(start_date.timestamp())
    end_seconds = round(end_date.timestamp())
    step = '15s'
    prometheus_query = f'sum (network_node_utilization_{line}_pct' + '{' + f'acn_id=~"{acn}",acc_id=~"{acc}",job="powerflex-edge-switchboard"' + '}) without(instance, pod, version)'
    query = f'query=last_over_time({prometheus_query})[5m]'
    return f'{config.SITE_METRICS_URL}/api/v1/query_range?{query}&start={start_seconds}&end={end_seconds}&step=${step}'


async def fetch_thanos_data(url: str):
    ...
