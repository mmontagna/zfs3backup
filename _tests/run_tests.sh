#!/bin/sh

FLAGS=""
export SKIP_CONFIG_FILE=true

if [ -n "$S3_KEY_ID" ]; then
    py.test
else
    py.test -k 'not with_s3'
fi
