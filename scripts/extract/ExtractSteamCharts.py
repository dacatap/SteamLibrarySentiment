import requests
from datetime import datetime, timezone
import json

def getSteamChartsHistory(steam_game_id : int) -> tuple[str, dict]:
    url = f"https://steamcharts.com/app/{steam_game_id}/chart-data.json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    raw_payload = response.json()
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    storage_key = f"raw/SteamCharts/playercounts/game_id={steam_game_id}/{fetch_date}.json"

    return storage_key, raw_payload
