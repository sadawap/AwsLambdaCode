# This code doenload the data from s3 bucket using GET function
# In this code the application/jpeg is set to download the binary data of jpeg images

import os
import logging
import json
import base64
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    
    try:
        # Validate API key
        api_key = event.get('headers', {}).get('x-api-key')
        my_key_value = os.environ.get("MY_KEY", None)
        if api_key != my_key_value:
            return {
                "statusCode": 403,
                "body": json.dumps("Forbidden: Invalid API Key")
            }
        
        bucket_name = os.environ.get("BUCKET_NAME", None)
        if event and bucket_name:
            s3 = boto3.client("s3")
            folder_name = event.get("pathParameters").get("myfolder")
            file_name = event.get("queryStringParameters").get("key")

            fileObj = s3.get_object(
                Bucket=bucket_name, Key=f"{folder_name}/{file_name}"
            )
            file_content = fileObj["Body"].read()

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/jpeg",
                    "Content-Disposition": "attachment; filename={}".format(file_name),
                },
                "body": base64.b64encode(file_content).decode('utf-8'),  # base64 encoded content should be decoded to string
                "isBase64Encoded": False  # Since we decoded the content, set this to False
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps("Invalid invocation or Bucket name is not defined!")
            }

    except Exception as e:
        logger.error(e)
        return {
            "statusCode": 500,
            "body": json.dumps("Error processing the request!")
        }