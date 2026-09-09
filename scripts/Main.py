import os
import time
import boto3
import datetime
from extract.ExtractSteam import getGameSteamNews, getGameSteamReviewHistory, getSteamLibrary
from extract.ExtractITAD import postITADGamesGetInfo, getITADGameInfo, getITADGameHistory
from extract.ExtractSteamCharts import getSteamChartsHistory
from load.LoadS3 import uploadToS3
from dotenv import load_dotenv

#Keys
load_dotenv()
steam_api_key = os.getenv("STEAM_API_KEY")
steam_id = os.getenv("STEAM_ID")
call_delay = float(os.getenv("CALL_DELAY"))
itad_api_key = os.getenv("ITAD_API_KEY")
itad_rate_limit = int(os.getenv("ITAD_itad_rate_limit"))
bucket_name = os.getenv("AWS_S3_BUCKET_NAME")

#TODO Temp functions

def getReleaseDate(steam_game_id: str) -> datetime:
    pass
def extractAndLoadData(steam_api_key, steam_id, itad_api_key, itad_rate_limit):
    #Extraction of Steam Library of personal account
    gamelist = getSteamLibrary(steam_api_key, steam_id)

    #Open S3 session
    s3_client = boto3.client(
        "s3",
        aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name= os.getenv("AWS_REGION_NAME")
    )
    #TODO
    #Missing Step: Check if game ID already exists in storage, if it does, eliminate from the processing batch. For now, new_games = gamelist
    
    #Check if game info exists in storage, if not, extract game info from ITAD API
    itad_map = postITADGamesGetInfo(gamelist, itad_api_key)
    for i, (steam_game_id, itad_id) in enumerate(itad_map.items(),start=1):
        storage_key, raw_payload = getITADGameInfo(steam_game_id, itad_id, itad_api_key)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        if i % itad_rate_limit == 0:
            time.sleep(300)

    #Extract Loop! Be wary of rate limits!!!
    #Keep count of the loop for the rate limit!!!!
    for game_id in gamelist:
        storage_key, raw_payload = getGameSteamReviewHistory(game_id)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        time.sleep(call_delay)
        storage_key, raw_payload = getGameSteamNews(game_id)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        time.sleep(call_delay)
        storage_key, raw_payload = getSteamChartsHistory(game_id)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)

        #ITAD price history
        itad_id = itad_map.get(str(game_id))
        release_date = getReleaseDate(game_id)

        storage_key, raw_payload = getITADGameHistory(itad_id, release_date, itad_api_key)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)

        time.sleep(call_delay-call_delay/3)
