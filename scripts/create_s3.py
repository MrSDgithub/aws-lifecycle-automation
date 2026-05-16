import boto3
import json
import logging
import time
from botocore.exceptions import ClientError
from config import REGION, BUCKET_PREFIX, STATE_FILE, LOG_FILE, TAGS

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_state():
    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)

def create_s3_bucket():
    s3 = boto3.client("s3", region_name=REGION)
    state = load_state()

    if "bucket_name" in state:
        print(f"S3 bucket already exists in state: {state['bucket_name']}")
        logging.info(f"S3 bucket already exists in state: {state['bucket_name']}")
        return state["bucket_name"]

    bucket_name = f"{BUCKET_PREFIX}-{int(time.time())}"

    try:
        print(f"Creating S3 bucket: {bucket_name}")

        if REGION == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    "LocationConstraint": REGION
                }
            )

        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            }
        )

        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }
        )

        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                "Status": "Enabled"
            }
        )

        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                "TagSet": [
                    {"Key": tag["Key"], "Value": tag["Value"]}
                    for tag in TAGS
                ]
            }
        )

        s3.put_object(
            Bucket=bucket_name,
            Key="project-info.txt",
            Body=b"This file was uploaded automatically by Python S3 automation."
        )

        state["bucket_name"] = bucket_name
        save_state(state)

        print(f"S3 bucket created successfully: {bucket_name}")
        print("Uploaded project-info.txt to S3 bucket.")

        logging.info(f"S3 bucket created successfully: {bucket_name}")

        return bucket_name

    except ClientError as error:
        print(f"ERROR: Failed to create S3 bucket: {error}")
        logging.error(f"Failed to create S3 bucket: {error}")
        raise

if __name__ == "__main__":
    create_s3_bucket()
