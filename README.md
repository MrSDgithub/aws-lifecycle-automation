# AWS EC2 and S3 Lifecycle Automation

## Project Overview

This project demonstrates cloud automation scripting using Python and Bash. It provisions AWS EC2 and S3 resources, generates status reports, logs execution details, waits for a fixed duration, and automatically stops the EC2 instance.

The project is designed as a simple cloud automation project for learning Python scripting, AWS SDK usage, Bash automation, logging, error handling, scheduled tasks, Git version control, and GitHub submission.

## Project Objective

The objective of this project is to automate cloud provisioning and lifecycle management tasks using Python and Bash scripts.

## Services Used

- AWS EC2
- AWS S3
- AWS CLI
- Python 3
- Boto3
- Bash
- Cron
- Git
- GitHub

## What the Automation Does

1. Creates an S3 bucket.
2. Enables S3 encryption.
3. Enables S3 versioning.
4. Blocks public access on the S3 bucket.
5. Uploads a sample file to S3.
6. Launches an EC2 instance.
7. Creates a security group.
8. Generates a before-stop status report.
9. Waits for a fixed number of seconds.
10. Automatically stops the EC2 instance.
11. Generates an after-stop status report.
12. Runs scheduled status reporting using cron.
13. Saves logs and output files.

## Important Note

EC2 is a compute service and can be stopped. S3 is an object storage service and does not have a stopped state. Therefore, this project automatically stops the EC2 instance and keeps the S3 bucket available for report storage and verification.

## Folder Structure

```text
aws-lifecycle-automation/
├── README.md
├── docs/
│   └── USAGE.md
├── logs/
│   ├── cron.log
│   └── project.log
├── outputs/
│   ├── state.json
│   ├── before_stop_report.json
│   └── after_stop_report.json
├── requirements.txt
└── scripts/
    ├── auto_stop.py
    ├── cleanup.py
    ├── config.py
    ├── create_ec2.py
    ├── create_s3.py
    ├── run_project.sh
    └── status_report.py
