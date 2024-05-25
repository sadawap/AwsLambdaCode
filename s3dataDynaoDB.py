# Code to create list and binary data of images and save it to dynamo db as image name and binary data in s3 bucket as txt file.

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
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ImageFiles')
        
        # List objects in the specified folder
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        
        if 'Contents' not in response:
            return {
                'statusCode': 200,
                'body': json.dumps('No files found in the specified folder')
            }
        
        image_files_metadata = {}
        
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Get the image file from S3
                image_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                image_data = image_obj['Body'].read()
                
                # Convert image data to base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # Save the base64 data back to S3 in a separate folder
                base64_file_key = f"base64-images/{file_key}.txt"
                s3.put_object(Bucket=bucket_name, Key=base64_file_key, Body=image_base64)
                
                # Add metadata to DynamoDB
                table.put_item(
                    Item={
                        'file_key': file_key,
                        'base64_s3_path': base64_file_key
                    }
                )
                
                # Collect metadata for response
                image_files_metadata[file_key] = base64_file_key
        
        return {
            'statusCode': 200,
            'body': json.dumps(image_files_metadata)
        }
    except Exception as e:
        logger.error("Error occurred: %s", e)
        return {
            'statusCode': 500,
            'body': json.dumps(f"Internal server error: {str(e)}")
        }
