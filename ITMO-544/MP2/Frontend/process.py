import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
from boto3.dynamodb.conditions import Key, Attr
import PIL.Image
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def resize_image(image_path, resized_path):
    with Image.open(image_path) as image:
        size = (100, 100)
        image.thumbnail(size)
        image.save(resized_path)

def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key1 = unquote_plus(record['s3']['object']['key'])
        logger.info(key1)

        splitRecipit = key1.split('-')
        Receipt1 = splitRecipit[0]
        key =splitRecipit[1]
        logger.info(Receipt1)
        logger.info(key)
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key1)
        upload_path = '/tmp/resized-{}'.format(key)

        logger.info('Downloading object {} from bucket {}'.format(key1, bucket))
        s3_client.download_file(bucket, key1, download_path)
        resize_image(download_path, upload_path)
        
        logger.info("resizeImage Finishe")
        logger.info(download_path)
        logger.info(upload_path)

        logger.info('Uploading object {} from bucket {}'.format(key1, bucket))
        s3_client.upload_file(upload_path, '{}resized'.format(bucket), key1,ExtraArgs={'ACL': 'public-read'})
        # url =  http://s3-REGION-.amazonaws.com/BUCKET-NAME/KEY
        
        url = "https://pal-544-raw-bucketresized.s3.amazonaws.com/"+key1 
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('RecordsPal')
        response = table.query(
            KeyConditionExpression=Key('Receipt').eq(Receipt1)
            )
        logger.info(response)
        email = response['Items'][0]['Email']
        number = response['Items'][0]['Phone']
        logger.info(email)


        dynamo_client = boto3.client(service_name='dynamodb')
        db_resp = dynamo_client.update_item(
            TableName='RecordsPal',
            Key={
                'Receipt': {'S': Receipt1},
                'Email': {'S':  email}
                },
            UpdateExpression="set S3finishedurl=:processed_url, #processed = :processed",
            ExpressionAttributeValues={
                ':processed_url': {'S': url},
                ':processed': {'BOOL': True}
                },
            ExpressionAttributeNames={"#processed": "Status"},
            ReturnValues="UPDATED_NEW"
            )
         
        logger.info("table is updated")
        client = boto3.client('sns')
        response=client.publish(
        PhoneNumber = number,
        Message="URL to Processed Image is" + key)




