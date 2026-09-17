import requests
from datetime import datetime, timezone
import json

def getSteamChartsHistory(steam_game_id: int) -> tuple[str, list]:
    url = f"https://steamcharts.com/app/{steam_game_id}/chart-data.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    raw = response.json()
    raw_payload = [{"timestamp": entry[0], "avg_players": entry[1]} for entry in raw]

    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    storage_key = f"raw/SteamCharts/playercounts/steam_game_id={steam_game_id}/{fetch_date}.parquet"

    return storage_key, raw_payload

