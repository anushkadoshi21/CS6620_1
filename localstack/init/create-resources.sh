#!/bin/bash
set -e

echo "Creating DynamoDB table 'clients'..."
awslocal dynamodb create-table \
  --table-name clients \
  --attribute-definitions AttributeName=name,AttributeType=S \
  --key-schema AttributeName=name,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

echo "Creating S3 bucket 'clients'..."
awslocal s3 mb s3://clients

echo "Init complete."chmod +x localstack/init/create-resources.sh