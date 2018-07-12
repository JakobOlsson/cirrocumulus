#!/bin/env python3
"""
    A tool for setting up infrastructure common resources
    Setup a new environment
    Deploy a configuration for a given environment
    Check current status of aviable deployment and resources
"""
import sys
import configparser
import boto3


def get_keypair_names():
    """ Returns a list of EC2 KeyPair Names """
    client = boto3.client('ec2')
    keypairs = client.describe_key_pairs().get('KeyPairs')
    if keypairs:
        return [x['KeyName'] for x in keypairs]
    return []


def create_keypair(name):
    """ Create an EC2 KeyPair with name - if it doesn't already exist """
    if name in get_keypair_names():
        print("Key:", name, "already exists")
    else:
        print("Creating key:", name)


def get_s3bucket_names():
    """
        Returns a list of S3 Buckets
        belonging to owner of current aws account
    """
    client = boto3.client('s3')
    bucketnames = client.list_buckets().get('Buckets')
    if bucketnames:
        return [x['Name'] for x in bucketnames]
    return []


def create_bucket(name):
    """ Create an S3 Bucket with name - if it doesn't already exist """
    if name in get_s3bucket_names():
        print("S3Bucket:", name, "already exists")
    else:
        print("Creating S3bucket:", name)


def get_stack_names():
    """ Returns a list of CloudFormation Stack names """
    client = boto3.client('cloudformation')
    stacknames = client.list_stacks().get('StackSummaries')
    if stacknames:
        return [x['StackName'] for x in stacknames]
    return []


def get_stack_info(name):
    """ Get a dictonary object with detailed info for stack with name """
    client = boto3.client('cloudformation')
    stackinfo = client.describe_stacks(StackName=name).get('Stacks')
    if stackinfo is not None:
        return stackinfo[0]


if __name__ == "__main__":
    if len(sys.argv) < 2 or "-h" in sys.argv[1]:
        print("Usage: deploy.py [option] <value>",
              "\n", "This is a simple script to bootstrap and/or",
              "\n", "update an aws environment",
              "\n", "It reads it's configuration form deploy.conf",
              "\n\n", "Options",
              "\n", " --help, -h\tPrints this help message"
              "\n", " --list-keys\tList existing EC2 Key Pair Names"
              "\n", " --create-key name\tCreate a EC2 Key Pair"
              "\n", " --list-buckets\tList existing s3 buckets"
              "\n", " --create-bucket name\tCreate a s3 bucket"
              "\n", " --upload\tUpload cloudformation scripts to s3 bucket"
              "\n", " --status name\tStatus for given environment"
              "\n", " --list-deploy\tlist deployed environments"
              "\n", " --deploy name\tDeploy/Update given environment")
    elif len(sys.argv) == 2:
        if "list-keys" in sys.argv[1]:
            print("Key Names:", ", ".join(get_keypair_names()))
        elif "list-buckets" in sys.argv[1]:
            print("Bucket Names:", ", ".join(get_s3bucket_names()))
        else:
            print("missing or wrong argument")

    else:
        if "create-key" in sys.argv[1]:
            create_keypair(sys.argv[2])
        elif "create-bucket" in sys.argv[1]:
            create_bucket(sys.argv[2])
