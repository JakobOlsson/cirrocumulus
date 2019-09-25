#!/usr/bin/env python3
import argparse
import os
import boto3


def get_parameters(base_path='/env/dev',
                   recursive=False,
                   region_name='eu-central-1'):
    '''
        gets all key-val pairs
        from a paramter store path
    '''
    cl = boto3.client('ssm',
                      region_name=os.environ.get('AWS_REGION', region_name))
    tok = None
    params = {}
    while 1:
        req = {'Path': base_path,
               'Recursive': recursive,
               'MaxResults': 10}
        if tok:
            req['NextToken'] = tok

        res = cl.get_parameters_by_path(**req)
        for param in res.get('Parameters', []):
            name = param.get('Name')
            val = param.get('Value')
            if name and val:
                name = name.split('/')[-1]
                params[name] = val

        tok = res.get('NextToken')
        if tok is None:
            break

    return params


def cli():
    '''
        Show the command line options

        Process given options and run the functions
    '''
    this_desc = 'Get parameters from parameter store and print lines on output as: export key=val'
    epi = '''
example: use the output in bash with
 eval "$(./get_parameters -c '/env/dev/dbs/database')"'''

    par = argparse.ArgumentParser(description=this_desc,
                                  epilog=epi,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)

    par.add_argument('-r', '--recursive',
                     action='store_true',
                     help='Get from path recursivily')
    par.add_argument('-c', '--capital-letters',
                     action='store_true',
                     help='capital letters for keys')
    par.add_argument('--no-export',
                     action='store_true',
                     help='dont start lines with: export')
    par.add_argument('--region',
                     nargs=1,
                     action='store',
                     default=['eu-central-1'],
                     help='which region')
    par.add_argument('path',
                     nargs=1,
                     help="parmater store path like /env/dev")
    par.add_argument('prefix',
                     nargs='?',
                     default='',
                     help="add prefix to key PREFIX_key=<val>")
    args = par.parse_args()
    parameter_path = args.path[0]
    prefix = args.prefix
    capitalize = args.capital_letters
    params = get_parameters(base_path=parameter_path,
                            recursive=args.recursive,
                            region_name=args.region[0])

    for key, val in params.items():
        key = key.replace('-', '_')
        if prefix != '':
            key = "{}_{}".format(prefix, key)
        if capitalize:
            key = key.upper()
        if args.no_export:
            print("{}={}".format(key, val))
        else:
            print("export {}={}".format(key, val))


if __name__ == '__main__':
    # use the output of this command in in bash
    # eval "$(./get_parameters '/path')"
    # to export them as environment vars
    cli()
