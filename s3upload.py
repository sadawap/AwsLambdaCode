# This code upload the content in S3 bucket.

import json
import base64
import boto3

def lambda_handler(event, context):
    
    print(event)
    
    s3 = boto3.client("s3")
    
    
    # retrieve data from event
    get_file_content = event["body-json"]
    
    # decode data
    decode_content = base64.b64decode(get_file_content)
    
    # upload file to s3
    s3_upload = s3.put_object(Bucket ="sadawap", Key="file.pdf", Body=decode_content)
    
    return {
        "StatusCode" : 200,
        "body" : "File has been uploaded"
    }
