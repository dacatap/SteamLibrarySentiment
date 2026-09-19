import requests
import time
from datetime import datetime, timezone
from typing import Any


#Retry wrapper
def get_with_retry(url, params=None, timeout=10, retries=3, backoff=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code in (403, 404):
                return None  # game unavailable, signal to skip
                
            response.raise_for_status()
            return response
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError):
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                raise

#GET game library dictionary
def getSteamLibrary(steam_api_key: str, steam_id: str) -> list[int]:
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"

    params = {
        "key": steam_api_key,
        "steamid": steam_id,
        "format": "json",
        "include_appinfo": 1
    }

    response = get_with_retry(url, params=params)
    if response is None:
        return None, None 
    response.raise_for_status()

    data = response.json()

    games = data.get("response", {}).get("games", [])
    game_id_list = [game["appid"] for game in games if not any(term in game.get("name", "").lower() for term in ["playtest", "beta", "demo", "test server", "technical test"])]

    return game_id_list


#GET review history (last 2 weeks) 
def getGameSteamReviewHistory(steam_game_id:int) -> tuple[str, dict[str, Any]]:
    url = f"https://store.steampowered.com/appreviewhistogram/{steam_game_id}"
    response = get_with_retry(url)
    if response is None:
        return None, None 
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

    response = get_with_retry(url, params=params)
    if response is None:
        return None, None 
    response.raise_for_status()

    #Same as previous function, raw payload to be stored into S3
    raw_payload = response.json()
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    storage_key = f"raw/Steam/news/steam_game_id={steam_game_id}/{fetch_date}.parquet"

    return storage_key, raw_payload