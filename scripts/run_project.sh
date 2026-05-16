#!/bin/bash

set -e

echo "Starting AWS EC2 and S3 Lifecycle Automation Project..."

cd /root/aws-lifecycle-automation
source venv/bin/activate

echo "Step 1: Creating S3 bucket..."
python scripts/create_s3.py

echo "Step 2: Launching EC2 instance..."
python scripts/create_ec2.py

echo "Step 3: Generating before-stop report..."
python scripts/status_report.py before

echo "Step 4: Waiting and automatically stopping EC2 instance..."
python scripts/auto_stop.py

echo "Step 5: Generating after-stop report..."
python scripts/status_report.py after

echo "Project automation completed successfully."
echo "Check logs/project.log"
echo "Check outputs/before_stop_report.json"
echo "Check outputs/after_stop_report.json"
