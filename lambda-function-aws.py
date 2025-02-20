import json
import boto3
import datetime

def lambda_handler(event, context):
    ec2=boto3.client('ec2')
    instances=ec2.describe_instances()
    cloudwatch=boto3.client('cloudwatch')
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    s3=boto3.client('s3')
    bucket_name = 'metrics-collectorbucket'
    file_name = 'metrics.json'
    
    instances = ec2.describe_instances()
    
    metrics=[]
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            cpu_metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(minutes=10),
                EndTime=datetime.datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            for data_point in cpu_metrics['Datapoints']:
                metrics.append({
                    'InstanceId': instance_id,
                    'Timestamp': data_point['Timestamp'].isoformat(),
                    'CPUUtilization': data_point['Average']
                })
    
    json_data = json.dumps(metrics)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=json_data)
    print(metrics)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
lambda_handler(1,1)