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
        payload = json.loads(event['body'])
        file_name = payload['fileName']
        part_number = int(payload['partNumber'])
        total_chunks = int(payload['totalChunks'])
        chunk = base64.b64decode(payload['chunk'])  # Decode Base64 chunk

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
            Body=chunk
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
            del upload_sessions[file_name]  # Clean up session
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
