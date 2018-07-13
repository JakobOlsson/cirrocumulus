#!/bin/env python3
"""
    A tool for setting up infrastructure common resources
    Setup a new environment
    Deploy a configuration for a given environment
    Check current status of aviable deployment and resources
"""
import sys
import os
import configparser
import pprint
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
        print("*** IMPLEMENT:", "creation of EC2 keypair")


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
        print("*** IMPLEMENT:", "creation of s3bucket")


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
    return {}


def get_config(environmentname, configfile='deploy.conf'):
    """
        Returns dict of settings from config file
        Or default setting
    """
    # Default Settings
    cnfg = {
                "region": "eu-west-1",
                "bucket_name": "cfg-bucket",
                "keypair_name": "BastionKey",
           }
    absolut_pathname = os.path.abspath(os.path.dirname(sys.argv[0]))
    configfile = os.path.join(absolut_pathname, configfile)

    if os.path.isfile(configfile):
        cp = configparser.ConfigParser()
        cp.read(configfile)
        section = 'DEFAULT'
        if environmentname and environmentname in cp:
            section = environmentname
        cnfg['region'] = cp.get(section,
                                'region',
                                fallback=cnfg['region'])
        cnfg['bucket_name'] = cp.get(section,
                                     'bucket_name',
                                     fallback=cnfg['bucket_name'])

        cnfg['keypair_name'] = cp.get(section,
                                      'keypair_name',
                                      fallback=cnfg['keypair_name'])
        cnfg['version'] = cp.get(section,
                                 'version',
                                 fallback='')
    return cnfg


def get_status(environmentname):
    """ Return a status of global and given environment """
    stts = {}
    cnfg = get_config(environmentname)
    stts['region'] = cnfg['region']
    stts['keypair'] = {'name': cnfg['keypair_name'],
                       'status':
                       cnfg['keypair_name'] in get_keypair_names()}
    stts['bucket_name'] = {'name': cnfg['bucket_name'],
                        'status':
                        cnfg['bucket_name'] in get_s3bucket_names()}

    stts['stacks'] = []
    stacks = get_stack_names()
    for stack in stacks:
        if environmentname not in stack:
            continue
        info = get_stack_info(stack)
        stts['stacks'].append({'name':
                               stack,
                               'satus':
                               info.get('StackStatus', 'N/A'),
                               'date':
                               info.get('LastUpdateTime', 'N/A'),
                               'tags':
                               info.get('Tags', [])})
    return stts


def get_deployed():
    """ Returns a list of deployed environments """
    dpld = []
    stacks = get_stack_names()
    for stack in stacks:
        # Don't check tangled stacks
        if '-' in stack:
            continue
        info = get_stack_info(stack)
        tags = info.get('Tags')
        for tagpair in tags:
            if 'environment' in tagpair.get('Key') \
               and not tagpair.get('Value') in dpld:
                    dpld.appen(tagpair.get('Value'))
                    break
    return dpld


def upload():
    """
        Upload cloudformation templates to configured s3 bucket
        Needs to get version somehow, git tag, or githash
    """
    cnfg = get_config(None)
    if cnfg['s3_bucket_name'] in get_s3bucket_names():
        print("*** IMPLEMENT:",
              "sync of cloudformation templates to s3 bucket/version")
    else:
        print("Configured S3 bucket:",
              cnfg['s3_bucket_name'],
              "is missing, please create with --create-bucket")
        return False
    return True


def deploy(environment):
    """
        Deploys or update a given environment
        Checks which version is defined for given environment
        check if given version is already deployed
        Check if templats for version are aviable in bucket
        Updates if already exists, otherwise creates
    """
    print("*** IMPLEMENT:",
          "deployment of an environment")


if __name__ == "__main__":
    # No option or help option
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
              "\n", " --list-deployed\tlist deployed environments"
              "\n", " --deploy name\tDeploy/Update given environment")

    # Single option with no value
    # Or option requiring a missing value
    elif len(sys.argv) == 2:
        if "list-keys" in sys.argv[1]:
            print("Key Names:", ", ".join(get_keypair_names()))
        elif "list-buckets" in sys.argv[1]:
            print("Bucket Names:", ", ".join(get_s3bucket_names()))
        elif "list-deployed" in sys.argv[1]:
            pp = pprint.PrettyPrinter(indent=3)
            pp.pprint(get_deployed())
        elif "upload" in sys.argv[1]:
            upload()
        else:
            print("wrong option or missing value, see --help")

    # Option with a value
    else:
        if "create-key" in sys.argv[1]:
            create_keypair(sys.argv[2])
        elif "create-bucket" in sys.argv[1]:
            create_bucket(sys.argv[2])
        elif "status" in sys.argv[1]:
            pp = pprint.PrettyPrinter(indent=3)
            pp.pprint(get_status(sys.argv[2]))
        elif "deploy" in sys.argv[1]:
            deploy(sys.argv[2])
        else:
            print("wrong option, see --help")
