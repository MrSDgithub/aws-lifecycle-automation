import boto3
import json
import logging
import time
from botocore.exceptions import ClientError
from config import REGION, STATE_FILE, LOG_FILE

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

def save_empty_state():
    with open(STATE_FILE, "w") as file:
        json.dump({}, file, indent=4)

def cleanup_resources():
    ec2 = boto3.client("ec2", region_name=REGION)
    s3 = boto3.resource("s3", region_name=REGION)

    state = load_state()

    instance_id = state.get("instance_id")
    sg_id = state.get("security_group_id")
    bucket_name = state.get("bucket_name")

    try:
        if instance_id:
            print(f"Terminating EC2 instance: {instance_id}")

            ec2.terminate_instances(
                InstanceIds=[instance_id]
            )

            waiter = ec2.get_waiter("instance_terminated")
            waiter.wait(InstanceIds=[instance_id])

            print("EC2 instance terminated successfully.")
            logging.info(f"EC2 instance terminated successfully: {instance_id}")

        if sg_id:
            print("Waiting before deleting security group...")
            time.sleep(20)

            try:
                ec2.delete_security_group(
                    GroupId=sg_id
                )

                print(f"Security group deleted successfully: {sg_id}")
                logging.info(f"Security group deleted successfully: {sg_id}")

            except ClientError as error:
                print(f"Security group deletion skipped or failed: {error}")
                logging.warning(f"Security group deletion skipped or failed: {error}")

        if bucket_name:
            print(f"Deleting S3 bucket and all objects: {bucket_name}")

            bucket = s3.Bucket(bucket_name)
            bucket.object_versions.delete()
            bucket.delete()

            print("S3 bucket deleted successfully.")
            logging.info(f"S3 bucket deleted successfully: {bucket_name}")

        save_empty_state()

        print("Cleanup completed successfully.")
        logging.info("Cleanup completed successfully.")

    except ClientError as error:
        print(f"ERROR: Cleanup failed: {error}")
        logging.error(f"Cleanup failed: {error}")
        raise

if __name__ == "__main__":
    cleanup_resources()
