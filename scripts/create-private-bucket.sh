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

echo "*** creating bucket: $BUCKET"
aws s3api create-bucket --acl private --bucket $BUCKET --region $AWS_DEFAULT_REGION --create-bucket-confugration LocationContraint="$AWS_DEFAULT_REGION" $PROFILE
