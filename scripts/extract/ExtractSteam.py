import requests
from datetime import datetime, timezone
from typing import Any

#GET game library dictionary
def getSteamLibrary(steam_api_key: str, steam_id: str) -> list[int]:
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"

    params = {
        "key": steam_api_key,
        "steamid": steam_id,
        "format": "json",
        "include_appinfo": 0
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    games = data.get("response", {}).get("games", [])
    game_id_list = [game["appid"] for game in games]

    return game_id_list


#GET review history (last 2 weeks) 
def getGameSteamReviewHistory(steam_game_id:int) -> tuple[str, dict[str, Any]]:
    url = f"https://store.steampowered.com/appreviewhistogram/{steam_game_id}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    # Raw payload ready to land directly into S3
    raw_payload = response.json()
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    storage_key = f"raw/Steam/reviews/steam_game_id={steam_game_id}/{fetch_date}.parquet"

    return storage_key, raw_payload

#GET Steam Newsletter entries, only ones by the dev/publisher
def getGameSteamNews(steam_game_id: int, count: int) -> tuple[str, dict[str, Any]]:
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"

    params = {
        "appid": steam_game_id,
        "count": count,
        "maxlength": 300,
        "format": "json",
        "feeds": "steam_community_announcements",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    #Same as previous function, raw payload to be stored into S3
    raw_payload = response.json()
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    storage_key = f"raw/Steam/news/steam_game_id={steam_game_id}/{fetch_date}.parquet"

    return storage_key, raw_payload