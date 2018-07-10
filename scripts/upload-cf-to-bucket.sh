#!/bin/env bash

BUCKET=$1
if [ -z $BUCKET ] || [ $BUCKET == "--help" ] || [ $BUCKET == "-h" ]; then
  echo "usage: $0 <bucketname>"
  echo "optional: --profile <profile>"
  exit
fi
if [ $2 == "--profile" ]; then
  PROFILE="$2 $3"
fi

echo "*** uploading cloudformation templates to bucket: $BUCKET"
aws s3 sync ../cf/ $BUCKET --region $AWS_DEFAULT_REGION $PROFILE
