# List all functions in lambda, their Runtime, last invocation time and any depricated warnings.

import boto3
import csv
import json
import warnings
from datetime import datetime
from io import StringIO

def get_last_invocation_time(function_name, region):
    # Initialize the CloudWatch Logs client
    logs_client = boto3.client('logs', region_name=region)

    try:
        # Get the log events for the function
        response = logs_client.describe_log_streams(
            logGroupName='/aws/lambda/' + function_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )

        # Extract and return the last invocation time
        if 'logStreams' in response and response['logStreams']:
            last_invocation_time = response['logStreams'][0].get('lastEventTimestamp')
            if last_invocation_time:
                last_invocation_time = datetime.fromtimestamp(last_invocation_time / 1000)  # Convert milliseconds to seconds
                return last_invocation_time
    except logs_client.exceptions.ResourceNotFoundException:
        pass  # Log group does not exist

    return None

def lambda_handler(event, context):
    # Specify the AWS region
    aws_region = 'us-east-1'  # Replace 'your-aws-region' with your desired AWS region, e.g., 'us-east-1'
    
    # Initialize the Lambda client
    lambda_client = boto3.client('lambda', region_name=aws_region)

    # Retrieve a list of Lambda functions
    response = lambda_client.list_functions()

     # Extract function names and runtimes
    function_info = []
    for function in response['Functions']:
        function_name = function['FunctionName']
        function_runtime = function['Runtime']
        last_invocation_time = get_last_invocation_time(function_name, aws_region)
        if last_invocation_time:
            function_info.append({'Function Name': function_name, 'Runtime': function_runtime, 'Last Invocation Time': last_invocation_time.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            function_info.append({'Function Name': function_name, 'Runtime': function_runtime, 'Last Invocation Time': 'No invocations found'})
            
    #  New lambda function to find deprecated lambda function       
    my_lambda = lambda x: x + 1
    deprecated_lambda = []

    # Use warnings to filter deprecation warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Call the lambda function to trigger any warnings
        my_lambda(1)
        # Check if any warning was raised and if it was a DeprecationWarning
        deprecated_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
    
    if deprecated_warnings:
        deprecated_lambda.append("The lambda function has been deprecated.")
    else:
        deprecated_lambda.append("The lambda function is not deprecated.")

    # Check for deprecated warnings
    deprecated_status = 'Yes' if deprecated_warnings else 'No'
        
    # Convert output to CSV format
    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=['Function Name', 'Runtime', 'Last Invocation Time', 'Deprecated Warnings'])
    csv_writer.writeheader()
    for info in function_info:
        csv_writer.writerow({**info, 'Deprecated Warnings': deprecated_status})
    
    # Write CSV data to a file
    csv_filename = 'lambda_info.csv'
    s3_key = f'lambda_function_info/{csv_filename}'  
    s3_bucket = 'sadawap'  
    s3_client = boto3.client('s3')

    s3_client.put_object(Body=csv_data.getvalue(), Bucket=s3_bucket, Key=s3_key)

    return {
        'statusCode': 200,
        'body': {
            'function_info': function_info,
            'runtime': function_runtime,
            'deprecated_lambda_info': deprecated_lambda,
            'deprecated_warnings': deprecated_warnings
            
        }
        
    }