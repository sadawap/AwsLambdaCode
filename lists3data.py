import os
import logging
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    try:
        bucket_name = os.environ.get("BUCKET_NAME", None)
        if event and bucket_name:
            s3 = boto3.client("s3")
            folder_name = event.get("pathParameters").get("folder", "")
            
            # List objects in the specified folder
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
            
            # Extract object keys from the response
            object_keys = [obj['Key'] for obj in response.get('Contents', [])]

            return {
                "statusCode": 200,
                "body": json.dumps({"objects": object_keys})
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