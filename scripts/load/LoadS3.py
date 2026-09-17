import boto3
import json
import os
import io
import pandas as pd

def uploadToS3(storage_key: str, raw_payload: dict, s3_client, bucket_name: str):
    df = pd.DataFrame(raw_payload) if isinstance(raw_payload, list) else pd.DataFrame([raw_payload])
    buffer = io.BytesIO()
    df.to_parquet(buffer, index = False)
    buffer.seek(0)
    s3_client.put_object(
        Bucket= bucket_name,
        Key = storage_key,
        Body = buffer.getvalue(),
        ContentType="application/json"
    )
