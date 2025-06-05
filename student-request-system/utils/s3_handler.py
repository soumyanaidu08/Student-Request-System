import boto3
from botocore.exceptions import NoCredentialsError

BUCKET_NAME = 'your-bucket-name'

s3 = boto3.client('s3')

def upload_to_s3(file_obj, filename):
    try:
        s3.upload_fileobj(file_obj, BUCKET_NAME, filename)
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
    except NoCredentialsError:
        return None
