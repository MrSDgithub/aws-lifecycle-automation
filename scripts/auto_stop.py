import boto3
import json
import logging
import time
from botocore.exceptions import ClientError
from config import REGION, STATE_FILE, LOG_FILE, AUTO_STOP_SECONDS

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

def stop_ec2_after_delay():
    ec2 = boto3.client("ec2", region_name=REGION)
    state = load_state()

    instance_id = state.get("instance_id")

    if not instance_id:
        print("No EC2 instance found in state file. Nothing to stop.")
        logging.warning("No EC2 instance found in state file.")
        return

    try:
        print(f"Waiting {AUTO_STOP_SECONDS} seconds before stopping EC2 instance...")
        logging.info(f"Waiting {AUTO_STOP_SECONDS} seconds before stopping EC2 instance: {instance_id}")

        time.sleep(AUTO_STOP_SECONDS)

        print(f"Stopping EC2 instance: {instance_id}")
        logging.info(f"Stopping EC2 instance: {instance_id}")

        ec2.stop_instances(
            InstanceIds=[instance_id]
        )

        print("Waiting for EC2 instance to reach stopped state...")
        waiter = ec2.get_waiter("instance_stopped")
        waiter.wait(InstanceIds=[instance_id])

        print(f"EC2 instance stopped successfully: {instance_id}")
        logging.info(f"EC2 instance stopped successfully: {instance_id}")

    except ClientError as error:
        print(f"ERROR: Failed to stop EC2 instance: {error}")
        logging.error(f"Failed to stop EC2 instance: {error}")
        raise

if __name__ == "__main__":
    stop_ec2_after_delay()
