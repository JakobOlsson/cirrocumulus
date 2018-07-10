#!/bin/env bash

KEYNAME=$1
PROFILE=$2
if [ -z $KEYNAME ] || [ $KEYNAME == "--help" ] || [ $KEYNAME == "-h" ]; then
  echo "usage: $0 <keyname>"
  echo "optional: --profile <profile>"
  exit
fi
if [ ! -z $PROFILE ]; then
  if [ $PROFILE == "--profile" ]; then
    PROFILE="$2 $3"
  fi
fi

echo "*** creating keypair: $KEYNAME"
aws ec2 create-key-pair --key-name $KEYNAME $PROFILE
