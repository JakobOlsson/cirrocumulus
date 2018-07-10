#!/bin/env bash

BUCKET=$1
PROFILE=$2
if [ -z $BUCKET ] || [ $BUCKET == "--help" ] || [ $BUCKET == "-h" ]; then
  echo "usage: $0 <bucketname> <region>"
  echo "optional: --profile <profile>"
  exit
fi
if [ ! -z $PROFILE ]; then
  if [ $PROFILE eq "--profile" ]; then
    PROFILE="$2 $3"
  fi
fi

echo "*** uploading cloudformation templates to bucket: $BUCKET"
aws s3 sync ../cf/ s3://$BUCKET --exclude "*.swp" $PROFILE
