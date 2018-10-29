#!/usr/bin/env python3
"""
    A tool for working with infrastructures resources

    Setup common resources like S3 Bucket and KeyPairs

    Setup a new environment or update existing environment
    Deploy a configuration for a given environment
    Check current status of deployments and resources
"""
import sys
import os
import configparser
import pprint
import boto3
import botocore


def get_keypair_names(environment):
    """ Returns a list of EC2 KeyPair Names """
    cfg = get_config(environment)
    reg = cfg.get('region')
    client = boto3.client('ec2', region_name=reg)
    keypairs = client.describe_key_pairs().get('KeyPairs')
    if keypairs:
        return [x['KeyName'] for x in keypairs]
    return []


def create_keypair(environment, name):
    """ Create an EC2 KeyPair with name - if it doesn't already exist """
    cfg = get_config(environment)
    reg = cfg.get('region')
    kpn = cfg.get('keypair_name')
    if kpn == '':
        print('ERROR: No keypair name configured')
    if name in get_keypair_names(environment):
        print("Key:", name, "already exists")
    else:
        print("Creating key:", name)
        client = boto3.client('ec2',region_name=reg)
        ekp = client.create_key_pair(KeyName=name)
        print("Created:", ekp.get('KeyName'))
        print("PrivateKey:\n", ekp.get('KeyMaterial', 'missing'))
        print("FingerPrint:", ekp.get('KeyFingerprint', 'missing'))


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
        client = boto3.client('s3')
        stb = client.create_bucket(ACL='private',
                                   Bucket=name,
                                   CreateBucketConfiguration={
                                       'LocationConstraint': 'EU'
                                   })
        print("Created:", stb.get('Location', 'missing'))


def get_stack_names(environment):
    """ Returns a list of CloudFormation Stack names """
    cfg = get_config(environment)
    reg = cfg.get('region')
    client = boto3.client('cloudformation', region_name=reg)
    stacks = client.list_stacks().get('StackSummaries', [])
    stacknames = []
    for stack in stacks:
        if 'DELETE' not in stack['StackStatus']:
            stacknames.append(stack['StackName'])
    return stacknames


def get_stack_info(environment, name):
    """ Get a dictonary object with detailed info for stack with name """
    cfg = get_config(environment)
    reg = cfg.get('region')
    client = boto3.client('cloudformation', region_name=reg)
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
    abs_pth = os.path.abspath(os.path.dirname(sys.argv[0]))
    configfile = os.path.join(abs_pth, configfile)

    if os.path.isfile(configfile):
        par = configparser.ConfigParser()
        par.read(configfile)
        section = 'DEFAULT'
        if environmentname and environmentname in par:
            section = environmentname
        cnfg['region'] = par.get(section,
                                 'region',
                                 fallback=cnfg['region'])
        cnfg['bucket_name'] = par.get(section,
                                      'bucket_name',
                                      fallback=cnfg['bucket_name'])

        cnfg['keypair_name'] = par.get(section,
                                       'keypair_name',
                                       fallback=cnfg['keypair_name'])
        cnfg['version'] = par.get(section,
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
                       cnfg['keypair_name'] in get_keypair_names(environmentname)}
    stts['bucket_name'] = {'name': cnfg['bucket_name'],
                           'status':
                           cnfg['bucket_name'] in get_s3bucket_names()}

    stts['stacks'] = []
    stacks = get_stack_names(environmentname)
    for stack in stacks:
        if environmentname not in stack:
            continue
        info = get_stack_info(environmentname, stack)
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
    stacks = get_stack_names('DEFAULT')
    for stack in stacks:
        # Don't check tangled stacks
        if '-' in stack:
            continue
        info = get_stack_info('DEFAULT', stack)
        tags = info.get('Tags')
        for tagpair in tags:
            if 'environment' in tagpair.get('Key') \
               and not tagpair.get('Value') in dpld:
                dpld.append(tagpair.get('Value'))
                break
    return dpld


def get_files(pth):
    """
        Get all the files, recursively for a given path - pth
        returns them in a list with relative path to given path
    """
    fls = []
    for fil in os.listdir(pth):
        full_pth = os.path.join(pth, fil)
        if os.path.isdir(full_pth):
            for pth_fil in get_files(full_pth):
                fls.append(os.path.join(fil, pth_fil))
        else:
            fls.append(fil)
    return fls


def upload(environment=None):
    """
        Upload cloudformation templates to configured s3 bucket
        Needs to get version somehow, git tag, or githash
    """
    cfg = get_config(environment)
    ver = cfg.get('version')
    s3b = cfg.get('bucket_name')
    if s3b in get_s3bucket_names():
        if s3b not in get_s3bucket_names():
            print("Missing s3 bucket:",
                  s3b,
                  "- please create with --create-bucket",
                  s3b)
            return False
        bas_pth = "" if ver == '' else ver
        client = boto3.client('s3')
        # Find the cloudformation templates path relative to the script
        pth = os.path.abspath(os.path.dirname(sys.argv[0]))
        pth = os.path.join(os.path.split(pth)[0],
                           'cf')
        # Uploading files
        for fil in get_files(pth):
            # DONT use os.path.join since path names in target
            # has to explicitly be /
            key = "/".join((bas_pth, fil))
            try:
                # checking tags doesnt seem to calculate a cost
                # so we use it to se if an object already exists
                client.get_object_tagging(Bucket=s3b,
                                          Key=key)
                print("Object exists:", key, "in", s3b)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print("Uploading:", key, "to", s3b)
                    client.upload_file(os.path.join(pth, fil),
                                       s3b,
                                       key)
                else:
                    raise e
    else:
        print("Configured S3 bucket:",
              s3b,
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
    cfg = get_config(environment)
    ver = cfg.get('version')
    s3b = cfg.get('bucket_name')
    kpn = cfg.get('keypair_name')
    reg = cfg.get('region')
    if ver != '' \
            and s3b in get_s3bucket_names() \
            and kpn in get_keypair_names(environment):
        print("We have config")
        upload(environment)
        client = boto3.client('cloudformation', region_name=reg)
        bas_tpl = "https://" + s3b + "s3.amazonaws.com/"

    else:
        print("Missing infrastructure or configuraiton",
              "\nplease run:",
              sys.argv[0],
              "--status",
              environment)
        return False
    print("*** IMPLEMENT:",
          "deployment of an environment:", environment)
    return True


def main():
    """
        Process command line arguments

        Print simple help
        Or call the appropiet function
    """
    prpr = pprint.PrettyPrinter(indent=3)
    # No option or help option
    if len(sys.argv) < 2 or "-h" in sys.argv[1]:
        print("Usage: deploy.py [option] <value>",
              "\n", "This is a simple script to bootstrap and/or",
              "\n", "update an aws environment",
              "\n", "It reads it's configuration form deploy.conf",
              "\n\n", "Options",
              "\n", " --help, -h\tPrints this help message"
              "\n", " --list-keys environment\tList existing EC2 Key Pair Names for environment"
              "\n", " --create-key environment\tCreate a EC2 Key Pair"
              "\n", " --list-buckets\tList existing s3 buckets"
              "\n", " --create-bucket name\tCreate a s3 bucket"
              "\n", " --upload\tUpload cloudformation scripts to s3 bucket"
              "\n", " --status environment\tStatus for given environment"
              "\n", " --list-deployed\tlist deployed environments"
              "\n", " --deploy environmentname\tDeploy/Update given environment")

    # Single option with no value
    # Or option requiring a missing value
    elif len(sys.argv) == 2:
        if "list-buckets" in sys.argv[1]:
            print("Bucket Names:", ", ".join(get_s3bucket_names()))
        elif "list-deployed" in sys.argv[1]:
            prpr.pprint(get_deployed())
        elif "upload" in sys.argv[1]:
            upload()
        else:
            print("wrong option or missing value, see --help")

    # Option with a value
    else:
        if "create-key" in sys.argv[1]:
            create_keypair(sys.argv[2])
        if "list-keys" in sys.argv[1]:
            print("Key Names:", ", ".join(get_keypair_names(sys.argv[2])))
        elif "create-bucket" in sys.argv[1]:
            create_bucket(sys.argv[2])
        elif "status" in sys.argv[1]:
            prpr.pprint(get_status(sys.argv[2]))
        elif "deploy" in sys.argv[1]:
            deploy(sys.argv[2])
        else:
            print("wrong option, see --help")


if __name__ == "__main__":
    main()
