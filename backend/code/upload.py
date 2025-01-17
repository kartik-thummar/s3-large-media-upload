import boto3
import os
import json
import base64

s3 = boto3.client('s3')
# BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_NAME = "video-app-data"

# Store active multipart upload sessions
upload_sessions = {}

def lambda_handler(event, context):
    try:
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
                'body': json.dumps('Multipart upload completed successfully!')
            }

        return {
            'statusCode': 200,
            'body': json.dumps('Chunk uploaded successfully!')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
