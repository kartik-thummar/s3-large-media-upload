import boto3
import json

s3 = boto3.client('s3')
BUCKET_NAME = "video-app-data"


def abort_upload(event):

    print(event)

    filename = event['queryStringParameters']['fileName']
    upload_id = event['queryStringParameters']['uploadId']
    
    # Abort the multipart upload
    response = s3.abort_multipart_upload(
        Bucket=BUCKET_NAME,
        Key=filename,
        UploadId=upload_id
    )
    print(response)
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Multipart upload aborted successfully",
            "uploadId": upload_id,
            "fileName": filename
        })
    }
