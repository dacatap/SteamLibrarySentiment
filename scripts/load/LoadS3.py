import boto3
import json
import os

def uploadToS3(storage_key: str, raw_payload: dict, s3_client, bucket_name: str):
    s3_client.put_object(
        Bucket= bucket_name,
        Key = storage_key,
        Body = json.dumps(raw_payload),
        ContentType="application/json"
    )