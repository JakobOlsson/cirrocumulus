#!/bin/env bash

BUCKET=$1
REGION=$2
PROFILE=$3
if [ -z $BUCKET ] || [ $BUCKET == "--help" ] || [ $BUCKET == "-h" ] || [ -z $REGION ]; then
  echo "usage: $0 <bucketname> <region>"
  echo "optional: --profile <profile>"
  exit
fi
if [ ! -n $PROFILE ]; then
  if [ $PROFILE == "--profile" ]; then
    PROFILE="$2 $3"
  fi
fi

echo "*** creating bucket: $BUCKET"
aws s3api create-bucket --acl private --bucket $BUCKET --create-bucket-configuration LocationConstraint="EU" --region $REGION $PROFILE
