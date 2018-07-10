#!/bin/env bash

KEYNAME=$1
if [ -z $KEYNAME ] || [ $KEYNAME == "--help" ] || [ $KEYNAME == "-h" ]; then
  echo "usage: $0 <keyname>"
  echo "optional: --profile <profile>"
  exit
fi
if [ $2 == "--profile" ]; then
  PROFILE="$2 $3"
fi

echo "*** creating keypair: $KEYNAME"
aws ec2 create-key-pair --key-name $KEYNAME $PROFILE
