import requests
from datetime import datetime, timezone
import json

def postITADGamesGetInfo(game_id_list: list, ITAD_api_key: str) -> dict:
    url = f"https://api.isthereanydeal.com/lookup/id/shop/61/v1"

    params = {
        "key": ITAD_api_key
    }

    #Payload must be a json of strings in the form of "'app/{game1id}', 'app/{game2id}'"
    payload = [f"app/{id_num}" for id_num in game_id_list]

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url= url, params=params, headers=headers, json= payload,timeout= 10)
    response.raise_for_status()

    #Clean response, wipe "app/" prefix from every steam game ID
    raw_data = response.json()
    SteamID_ITADID = {key.removeprefix("app/"): value for key, value in raw_data.items()}

    return SteamID_ITADID

def getITADGameInfo(steam_app_id: str, game_ITAD_id: str, ITAD_api_key: str) -> tuple[str, dict]:
    url = "https://api.isthereanydeal.com/games/info/v2"
    params = {
        "id": game_ITAD_id,
        "shops": 61,
        "key": ITAD_api_key
    }
    response = requests.get(url=url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    raw_data = {
        "steam_appid": steam_app_id,
        "title": data.get("title"),
        "releaseDate": data.get("releaseDate")
    }

    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    storage_key = f"raw/ITAD/gameinfo/game_id={steam_app_id}/{fetch_date}.json"

    return storage_key, raw_data

def getITADGameHistory(steam_app_id: str, game_ITAD_id: str, release_date: str, ITAD_api_key: str) -> tuple[str, dict]:
    url = "https://api.isthereanydeal.com/games/history/v2"
    
    params = {
        "id": game_ITAD_id,
        "shops": 61,
        "key": ITAD_api_key,
        "since": f"{release_date}T00:00:00Z" if release_date else None
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    raw_payload = response.json()
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    storage_key = f"raw/ITAD/gamehistoricalsales/game_id={steam_app_id}/{fetch_date}.json"

    return storage_key, raw_payload 