#!/usr/bin/env bash

set -e

BUCKET=`aws ssm get-parameter --name default-sam-bucket --query Parameter.Value --output text`

pip3 install beautifulsoup4 --upgrade -t cfn-news/code/

aws cloudformation package --template-file templates/cfn-news.yaml --s3-bucket ${BUCKET} --s3-prefix serverlessrepo --output-template-file templates/cfn-news-packaged-template.yaml

sam publish --template templates/cfn-news-packaged-template.yaml --region us-east-1
