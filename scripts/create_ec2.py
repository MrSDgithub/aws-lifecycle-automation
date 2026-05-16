import boto3
import json
import logging
from botocore.exceptions import ClientError
from config import REGION, INSTANCE_TYPE, STATE_FILE, LOG_FILE, TAGS

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

def get_latest_amazon_linux_ami():
    ssm = boto3.client("ssm", region_name=REGION)
    response = ssm.get_parameter(
        Name="/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
    )
    return response["Parameter"]["Value"]

def create_security_group(ec2, vpc_id):
    group_name = "lifecycle-auto-sg"

    existing_groups = ec2.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [group_name]},
            {"Name": "vpc-id", "Values": [vpc_id]}
        ]
    )["SecurityGroups"]

    if existing_groups:
        sg_id = existing_groups[0]["GroupId"]
        print(f"Security group already exists: {sg_id}")
        logging.info(f"Security group already exists: {sg_id}")
        return sg_id

    response = ec2.create_security_group(
        GroupName=group_name,
        Description="Security group for EC2 auto stop automation project",
        VpcId=vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "security-group",
                "Tags": TAGS
            }
        ]
    )

    sg_id = response["GroupId"]

    print(f"Security group created: {sg_id}")
    logging.info(f"Security group created: {sg_id}")

    return sg_id

def launch_ec2_instance():
    ec2 = boto3.client("ec2", region_name=REGION)
    state = load_state()

    if "instance_id" in state:
        print(f"EC2 instance already exists in state: {state['instance_id']}")
        logging.info(f"EC2 instance already exists in state: {state['instance_id']}")
        return state["instance_id"]

    try:
        vpcs = ec2.describe_vpcs(
            Filters=[
                {"Name": "is-default", "Values": ["true"]}
            ]
        )["Vpcs"]

        if not vpcs:
            raise Exception("No default VPC found in this region.")

        vpc_id = vpcs[0]["VpcId"]
        sg_id = create_security_group(ec2, vpc_id)
        ami_id = get_latest_amazon_linux_ami()

        user_data = """#!/bin/bash
echo 'EC2 instance created by lifecycle automation project' > /home/ec2-user/project.txt
yum update -y
"""

        print("Launching EC2 instance...")

        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=INSTANCE_TYPE,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[sg_id],
            UserData=user_data,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": TAGS + [
                        {"Key": "Name", "Value": "lifecycle-auto-ec2"}
                    ]
                }
            ]
        )

        instance_id = response["Instances"][0]["InstanceId"]

        state["instance_id"] = instance_id
        state["security_group_id"] = sg_id
        save_state(state)

        print(f"EC2 instance launched successfully: {instance_id}")
        logging.info(f"EC2 instance launched successfully: {instance_id}")

        print("Waiting for EC2 instance to reach running state...")
        waiter = ec2.get_waiter("instance_running")
        waiter.wait(InstanceIds=[instance_id])

        print("EC2 instance is now running.")
        logging.info(f"EC2 instance is now running: {instance_id}")

        return instance_id

    except ClientError as error:
        print(f"ERROR: Failed to launch EC2 instance: {error}")
        logging.error(f"Failed to launch EC2 instance: {error}")
        raise

if __name__ == "__main__":
    launch_ec2_instance()
