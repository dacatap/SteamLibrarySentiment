import os
from dotenv import load_dotenv

load_dotenv()
steam_api_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")

"""
id_map = POSTITADGamesGetInfo(game_id_list, api_key)

for steam_id, itad_id in id_map.items():
    raw_data, path = GETITADGameInfo(steam_id, itad_id, api_key)
    # save_to_storage(raw_data, path)

"""