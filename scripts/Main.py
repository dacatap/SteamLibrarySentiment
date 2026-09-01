import os
import time
import datetime
from dotenv import load_dotenv
from extract.ExtractSteamCharts import getSteamChartsHistory
from extract.ExtractSteam import getGameSteamNews, getGameSteamReviewHistory, getSteamLibrary
from extract.ExtractITAD import postITADGamesGetInfo, getITADGameInfo, getITADGameHistory

#Keys
load_dotenv()
steam_api_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")
call_delay = float(os.getenv("CALL_DELAY"))
itad_api_key = os.getenv("ITAD_API_KEY")
itad_rate_limit = int(os.getenv("ITAD_RATE_LIMIT"))



#TODO Temp functions
def uploadS3(st_k, rw_pl):
    pass

def getReleaseDate(steam_game_id: str) -> datetime:
    pass
def extractData(steam_api_key, steam_id, itad_api_key, itad_rate_limit):
    #Extraction of Steam Library of personal account
    gamelist = getSteamLibrary(steam_api_key, steam_id)

    #TODO
    #Missing Step: Check if game ID already exists in storage, if it does, eliminate from the processing batch. For now, new_games = gamelist
    
    #Check if game info exists in storage, if not, extract game info from ITAD API
    itad_map = postITADGamesGetInfo(gamelist, itad_api_key)
    for i, (steam_game_id, itad_id) in enumerate(itad_map.items(),start=1):
        storage_key, raw_payload = getITADGameInfo(steam_game_id, itad_id, itad_api_key)
        uploadS3(storage_key, raw_payload)
        if i % itad_rate_limit == 0:
            time.sleep(300)

    #Extract Loop! Be wary of rate limits!!!
    for game_id in gamelist:
        storage_key, raw_payload = getGameSteamReviewHistory(game_id)
        uploadS3(storage_key, raw_payload)

        storage_key, raw_payload = getGameSteamNews(game_id)
        uploadS3(storage_key, raw_payload)

        storage_key, raw_payload = getSteamChartsHistory(game_id)
        uploadS3(storage_key, raw_payload)

        #ITAD price history
        itad_id = itad_map.get(str(game_id))
        release_date = getReleaseDate(game_id)

        storage_key, raw_payload = getITADGameHistory(itad_id, release_date, itad_api_key)
        uploadS3(storage_key, raw_payload)

        time.sleep(call_delay)
