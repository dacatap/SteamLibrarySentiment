import io
import os
import time
import json
import boto3
import datetime
import pandas as pd
from extract.ExtractSteam import getGameSteamNews, getGameSteamReviewHistory, getSteamLibrary
from extract.ExtractITAD import postITADGamesGetInfo, getITADGameInfo, getITADGameHistory
from extract.ExtractSteamCharts import getSteamChartsHistory
from load.LoadS3 import uploadToS3
from dotenv import load_dotenv

###Function definitions
#Query to s3 to check both, if games exist in registers, and return their release date if they do!
#May need to move this function to a dedicated script for organization in case more "queries" are made to the bucket in the transform step
def getGamesInfoBucket(steam_game_id_list: list, s3_client, bucket_name: str) -> tuple[dict, list]:
    games_info = {}
    new_games = []

    for game_id in steam_game_id_list:
        #Note: Although this works, in case that in the future ITAD adds more fields to the response of "/games/info/v2", the better alternative would be to have the prefix be:
        #prefix = f"raw/ITAD/gameinfo/steam_game_id={game_id}/" and modify the storage_key of getITADGameInfo to store the parquet file as "{prefix}{fetch_date}.parquet"
        #That way, if data gets enriched, we can have a record of how it has been enriched through time, in case that was ever a consideration of the scope.
        prefix = f"raw/ITAD/gameinfo/steam_game_id={game_id}.parquet"
        
        try:
            obj = s3_client.get_object(Bucket=bucket_name, Key=prefix)
            buffer = io.BytesIO(obj["Body"].read())
            df = pd.read_parquet(buffer)
            row = df.iloc[0]
            games_info[str(game_id)] = (row["itad_id"], row["releaseDate"])
        except s3_client.exceptions.NoSuchKey:
            new_games.append(game_id)

    return games_info, new_games

def extractAndLoadData(steam_api_key, steam_id, call_delay, itad_api_key, itad_rate_limit, aws_access_key_id, aws_secret_access_key,  region_name, bucket_name):
    #Extraction of Steam Library of personal account
    #gamelist = getSteamLibrary(steam_api_key, steam_id)

    gamelist = [2054970, 1245620, 1850570]
    #Open S3 session
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    #Check if games already have info in s3 bucket
    games_info, new_games = getGamesInfoBucket(gamelist, s3_client, bucket_name)
    if new_games:
        itad_map = postITADGamesGetInfo(new_games, itad_api_key)
        for i, (steam_game_id, itad_id) in enumerate(itad_map.items(), start=1):
            storage_key, raw_payload = getITADGameInfo(steam_game_id, itad_id, itad_api_key)
            games_info[steam_game_id] = (raw_payload["itad_id"], raw_payload["releaseDate"])
            uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
            if i % itad_rate_limit == 0:
                time.sleep(300)

    #Extract Loop! Be wary of rate limits!!!
    #In practice, the call_delay will keep us under the reported steam rate limits, and well behind ITAD's API rate limits, still, monitor with attention!!!
    for game_id in gamelist:
        storage_key, raw_payload = getGameSteamReviewHistory(game_id)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        time.sleep(call_delay)
        storage_key, raw_payload = getGameSteamNews(game_id, 100)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        time.sleep(call_delay)
        storage_key, raw_payload = getSteamChartsHistory(game_id)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)

        #ITAD price history
        itad_id, release_date = games_info[str(game_id)]

        storage_key, raw_payload = getITADGameHistory(game_id, itad_id, release_date, itad_api_key)
        uploadToS3(storage_key, raw_payload, s3_client, bucket_name)
        time.sleep(call_delay-call_delay/3)


###Main execution
def main():
    #Keys
    load_dotenv()
    steam_api_key = os.getenv("STEAM_API_KEY")
    steam_id = os.getenv("STEAM_ID")
    call_delay = float(os.getenv("CALL_DELAY"))
    itad_api_key = os.getenv("ITAD_API_KEY")
    itad_rate_limit = int(os.getenv("ITAD_RATE_LIMIT"))
    aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key= os.getenv("AWS_SECRET_ACCESS_KEY")
    region_name= os.getenv("AWS_REGION_NAME")
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    extractAndLoadData(steam_api_key, steam_id, call_delay, itad_api_key, itad_rate_limit, aws_access_key_id, aws_secret_access_key,  region_name, bucket_name)

main()