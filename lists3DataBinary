# working code : List all files and with binary data

import os
import logging
import json
import boto3
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    try:
        bucket_name = os.environ.get("BUCKET_NAME", None)
        if not bucket_name:
            raise ValueError("Bucket name is not set in environment variables")
        
        if not event or 'pathParameters' not in event or 'folder' not in event['pathParameters']:
            raise ValueError("Folder path is not specified in the event")
        
        folder_name = event['pathParameters']['folder']
        s3 = boto3.client("s3")
        
        # List objects in the specified folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        
        if 'Contents' not in response:
            return {
                'statusCode': 200,
                'body': json.dumps('No files found in the specified folder')
            }
        
        image_files_base64 = {}
        
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Get the image file from S3
                image_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                image_data = image_obj['Body'].read()
                
                # Convert image data to base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # Add the base64 data to the dictionary
                image_files_base64[file_key] = image_base64
        
        return {
            'statusCode': 200,
            'body': json.dumps(image_files_base64)
        }
    except Exception as e:
        logger.error("Error occurred: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
