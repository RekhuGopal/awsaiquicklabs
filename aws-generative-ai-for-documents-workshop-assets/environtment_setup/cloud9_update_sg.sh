#!/bin/bash

# Get the EC2 instance ID associated with the Cloud9 environment
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

# Get the security group associated with the EC2 instance
SECURITY_GROUP_ID=$(aws ec2 describe-instances --instance-id $INSTANCE_ID --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)

# Add a custom rule to allow ingress on port 8501 from anywhere
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 8501-8520 --cidr 0.0.0.0/0 

echo "Ingress rule for port 8501-8520 added to security group $SECURITY_GROUP_ID"