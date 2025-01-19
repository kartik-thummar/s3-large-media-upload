import boto3
from botocore.exceptions import ClientError
import os
import json
import base64

# session = boto3.Session(profile_name='kartik')
session = boto3.Session()
s3 = session.client('s3')

# BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_NAME = "video-app-data"

# Store active multipart upload sessions
upload_sessions = {}

def lambda_handler(event, context):
    # try:
        # print(event)
        print("event['body'] : ", event['body'])
        # Parse JSON payload from request
        # payload = json.loads(event['body'])
        file_name = event['queryStringParameters']['fileName']
        part_number = int(event['queryStringParameters']['partNumber'])
        total_chunks = int(event['queryStringParameters']['totalChunks'])
        # chunk = base64.b64decode(event['queryStringParameters']['chunk'])  # Decode Base64 chunk

        # Get the binary data from the request body
        binary_data = base64.b64decode(event['body']) if event['isBase64Encoded'] else event['body'].encode('utf-8')

        # Initialize multipart upload (for the first chunk)
        if part_number == 1:
            response = s3.create_multipart_upload(Bucket=BUCKET_NAME, Key=file_name)
            upload_id = response['UploadId']
            upload_sessions[file_name] = {
                'UploadId': upload_id,
                'Parts': []
            }
        else:
            # Retrieve existing session
            upload_id = upload_sessions[file_name]['UploadId']
            # upload_id = "iEYSTAMfRbJsMtemJXbw8J0TMPswiXoLh7ZJMOIhjVd4v62OHZ1.yR3AD2QxpjWgH0.sC1FRrvJnyGi9n8Kh2A178tXDjlX9sWe4u5dsJnWAepbqhlLz4wRCmJ.0Ho1ZDEEcQve_dKM3ufdW1q0khA--"

        # Upload the chunk
        upload_response = s3.upload_part(
            Bucket=BUCKET_NAME,
            Key=file_name,
            PartNumber=part_number,
            UploadId=upload_id,
            Body=binary_data
        )

        # Save the ETag for the uploaded part
        upload_sessions[file_name]['Parts'].append({
            'ETag': upload_response['ETag'],
            'PartNumber': part_number
        })
        print(upload_sessions)
        # Complete the upload if all chunks are uploaded
        if part_number == total_chunks:
            parts = upload_sessions[file_name]['Parts']
            s3.complete_multipart_upload(
                Bucket=BUCKET_NAME,
                Key=file_name,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            # del upload_sessions[file_name]  # Clean up session
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message':'Multipart upload completed successfully!',
                    'uploadId': upload_id
                    })
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message':'Chunk uploaded successfully!',
                'uploadId': upload_id           
                })
        }
    # except ClientError as e:
    #     print(e.with_traceback())
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps(str(e))
    #     }
        
    # except Exception as e:
    #     print(e)
    #     print(e.args)
    #     return {
    #         'statusCode': 500,
    #         'body': json.dumps(str(e))
    #     }
