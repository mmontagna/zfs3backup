#!/bin/sh

FLAGS=""
export SKIP_CONFIG_FILE=true

if [ -n "$SKIP_S3" ]; then
    py.test -k 'not with_s3'
else
    py.test
fi
