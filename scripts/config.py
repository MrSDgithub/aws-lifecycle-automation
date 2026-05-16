import os

REGION = os.getenv("AWS_REGION", "us-east-2")

PROJECT_NAME = "aws-lifecycle-automation"
OWNER = "Souhardya-De"

STATE_FILE = "outputs/state.json"
LOG_FILE = "logs/project.log"

BEFORE_STOP_REPORT = "outputs/before_stop_report.json"
AFTER_STOP_REPORT = "outputs/after_stop_report.json"

BUCKET_PREFIX = "souhardya-lifecycle-auto"

INSTANCE_TYPE = "t3.micro"

AUTO_STOP_SECONDS = 120

TAGS = [
    {"Key": "Project", "Value": PROJECT_NAME},
    {"Key": "Owner", "Value": OWNER},
    {"Key": "ManagedBy", "Value": "Python-Bash-Automation"},
    {"Key": "Purpose", "Value": "EC2-S3-Auto-Stop-Demo"}
]
