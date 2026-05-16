import boto3
import json
import logging
import sys
from datetime import datetime
from botocore.exceptions import ClientError
from config import REGION, STATE_FILE, LOG_FILE, BEFORE_STOP_REPORT, AFTER_STOP_REPORT

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

def generate_report(stage):
    ec2 = boto3.client("ec2", region_name=REGION)
    s3 = boto3.client("s3", region_name=REGION)

    state = load_state()

    if stage == "before":
        report_file = BEFORE_STOP_REPORT
    elif stage == "after":
        report_file = AFTER_STOP_REPORT
    else:
        report_file = "outputs/status_report.json"

    report = {
        "project": "AWS EC2 and S3 Lifecycle Automation",
        "region": REGION,
        "stage": stage,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "s3": {},
        "ec2": {}
    }

    try:
        bucket_name = state.get("bucket_name")

        if bucket_name:
            objects = s3.list_objects_v2(Bucket=bucket_name)

            report["s3"] = {
                "bucket_name": bucket_name,
                "object_count": objects.get("KeyCount", 0),
                "status": "Available",
                "note": "S3 is object storage and cannot be stopped like EC2."
            }
        else:
            report["s3"] = {
                "status": "No S3 bucket found in state file."
            }

        instance_id = state.get("instance_id")

        if instance_id:
            response = ec2.describe_instances(
                InstanceIds=[instance_id]
            )

            instance = response["Reservations"][0]["Instances"][0]

            report["ec2"] = {
                "instance_id": instance_id,
                "instance_type": instance["InstanceType"],
                "state": instance["State"]["Name"],
                "private_ip": instance.get("PrivateIpAddress", "N/A"),
                "public_ip": instance.get("PublicIpAddress", "N/A")
            }
        else:
            report["ec2"] = {
                "status": "No EC2 instance found in state file."
            }

        with open(report_file, "w") as file:
            json.dump(report, file, indent=4)

        if bucket_name:
            s3.upload_file(report_file, bucket_name, report_file.split("/")[-1])

        print(json.dumps(report, indent=4))
        print(f"Report saved to: {report_file}")

        logging.info(f"{stage} report generated successfully: {report_file}")

    except ClientError as error:
        print(f"ERROR: Failed to generate status report: {error}")
        logging.error(f"Failed to generate status report: {error}")
        raise

if __name__ == "__main__":
    stage = "normal"

    if len(sys.argv) > 1:
        stage = sys.argv[1]

    generate_report(stage)
