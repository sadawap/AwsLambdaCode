# This code retrieve the running ec2 instances ID and public key using path parameter and model in API gateway.

import json
import boto3

def lambda_handler(event, context):
    
    print(event)
    
    status = event["body-json"]["status"]
    

    ec2_client = boto3.client('ec2')
    
    response1 = ec2_client.describe_instances()
    
    running_instances = []
    instance_ip_address = []
    
    for ec2_instance in response1['Reservations']:
        for value in ec2_instance['Instances']:
            
            if value['State']['Name'] == 'running':
                running_instances.append(value['InstanceId'])
                instance_ip_address.append(value['PublicIpAddress'])
                
                response = {
                "Running Instances" : [
                {
                'Instance ID of instance is' : running_instances
                
                }],
                "Instance PUIP" : [
                {
                    'Instance IP address is' : instance_ip_address
                }]
                }    
            
            else:
                response = {
                "Running Instances" : [
                {
                'Instance ID of instance is' : "No running Instances"
                
                }],
                "Instance PIP" : [
                {
                    'Instance IP address is' : "No running instances"
                }]
            }    
        
    
    return {
        
        'body' : response[status]
    }