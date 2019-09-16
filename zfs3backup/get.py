import argparse
import sys

import boto.s3
import boto3

from zfs3backup.config import get_config


def download(bucket, name):
    bucket.download_fileobj(name, sys.stdout)


def main():
    cfg = get_config()
    parser = argparse.ArgumentParser(
        description='Read a key from s3 and write the content to stdout',
    )
    parser.add_argument('name', help='name of S3 key')
    args = parser.parse_args()

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(cfg['BUCKET'])

    download(bucket, args.name)

if __name__ == '__main__':
    main()
