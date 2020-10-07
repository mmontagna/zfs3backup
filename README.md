<!-- # zfs3backup [![Build Status](https://travis-ci.org/PressLabs/zfs3backup.svg)](https://travis-ci.org/PressLabs/zfs3backup)
 -->

This was forked from https://github.com/Presslabs/z3 which appears to be a dead project.

# Welcome to zfs3backup

zfs3backup is a ZFS to S3 backup tool. This is basically plumbing around `zfs send` and `zfs receive`
so you should have at least a basic understanding of what those commands do.


## Usage
`zfs3backup status` will show you the current state, what snapshots you have on S3 and on the local
zfs dataset.

`zfs3backup backup` perform full or incremental backups of your dataset.

`zfs3backup restore` restores your dataset to a certain snapshot.

See `zfs SUBCOMMAND --help` for more info.

### Installing
`pip install zfs3backup`

zfs3backup is tested on python 2.7.

#### Optional dependencies
```
# Install pv to get some progress indication while uploading.
apt-get install pv

# Install pigz to provide the pigz compressors.
apt-get install pigz
```

### Configuring
Most options can be configured as command line flags, environment variables or in a config file,
in that order of precedence.
The config file is read from `/etc/zfs3backup_backup/zfs3backup.conf` if it exists, some defaults are provided by the tool.
For a list of all options see `zfs3backup/sample.conf`.

You'll usually want zfs3backup to only backup certain snapshots (hourly/daily/weekly).
To do that you can specify a `SNAPSHOT_PREFIX` (defaults to `zfs-auto-snap:daily`).

Defaults for `SNAPSHOT_PREFIX` and `COMPRESSOR` can be set per filesystem like so:
```
[fs:tank/spam]
SNAPSHOT_PREFIX=delicious-daily-spam
COMPRESSOR=pigz4

[fs:tank/ham]
SNAPSHOT_PREFIX=weekly-non-spam
```

#### S3 Credentials

This package uses boto3's standard credential chain for s3 credentials see: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

### Dataset Size, Concurrency and Memory Usage
Since the data is streamed from `zfs send` it gets read in to memory in chunks.
zfs3backup estimates a good chunk size for you: no smaller than 5MB and large enough
to produce at most 9999 chunks. These are S3 limitation for multipart uploads.
Here are some example chunk sizes for different datasets:
 * 50 GiB: 5 MiB
 * 500 GIB: 53 MiB
 * 1 TiB: 110 MiB
 * 2 TiB: 220 MiB

Multiply that by `CONCURRENCY` to know how much memory your upload will use.

### Usage Examples

#### Status
```
# show global options
zfs3backup --help

# show status of backups for default dataset
zfs3backup status

# show status for other dataset; only snapshots named daily-spam-*
zfs3backup --dataset tank/spam --snapshot-prefix daily-spam- status
```

#### Backup
```
# show backup options
zfs3backup backup --help

# perform incremental backup the latest snapshot; use pigz4 compressor
zfs3backup backup --compressor pigz4 --dry-run
# inspect the commands that would be executed
zfs3backup backup --compressor pigz4

# perform full backup of a specific snapshot
zfs3backup backup --full --snapshot the-part-after-the-at-sign --dry-run
# inspect the commands that would be executed
zfs3backup backup --full --snapshot the-part-after-the-at-sign
```

#### Restore
```
# see restore options
zfs3backup restore --help

# restore a dataset to a certain snapshot
zfs3backup restore the-part-after-the-at-sign --dry-run
# inspect the commands that would be executed
zfs3backup restore the-part-after-the-at-sign

# force rollback of filesystem (zfs recv -F)
zfs3backup restore the-part-after-the-at-sign --force
```

### Other Commands
Other command line tools are provided.

`pput` reads a stream from standard in and uploads the data to S3.

`zfs3backup_ssh_sync` a convenience tool to allow you to push zfs snapshots to another host.
If you need replication you should checkout zrep. This exists because we've already
got zrep between 2 nodes and needed a way to push backups to a 3rd machine.

`zfs3backup_get` called by `zfs3backup restore` to download a backup.

## Development Overview
### Running the tests
The test suite uses pytest.
Some of the tests upload data to S3, so you need to setup the following environment:
```
export S3_KEY_ID=""
export S3_SECRET=""
export BUCKET="mytestbucket"
```

To skip tests that use S3:
```
py.test --capture=no --tb=native _tests/ -k "not with_s3"
```

### The Data
Snapshots are obtained using `zfs send`, optionally piped trough a compressor (pigz by default),
and finally piped to `pput`.
Incremental snapshots are always handled individually, so if you have multiple snapshots to send
since the last time you've performed a backup they get exported as individual snapshots
(multiple calls to `zfs send -i dataset@snapA dataset@snapB`).

Your snapshots end up as individual keys in an s3 bucket, with a configurable prefix (`S3_PREFIX`).
S3 key metadata is used to identify if a snapshot is full (`isfull="true"`) or incremental.
The parent of an incremental snapshot is identified with the `parent` attribute.

S3 and ZFS snapshots are matched by name.

### Health checks
The S3 health checks are very rudimentary, basically if a snapshot is incremental check
that the parent exists and is healthy. Full backups are always assumed healthy.

If backup/restore encounter unhealthy snapshots they abort execution.

### pput
pput is a simple tool with one job, read data from stdin and upload it to S3.
It's usually invoked by zfs3backup.

Consistency is important, it's better to fail hard when something goes wrong
than silently upload inconsistent or partial data.
There are few anticipated errors (if a part fails to upload, retry MAX_RETRY times).
Any other problem is unanticipated, so just let the tool crash.

TL;DR Fail early, fail hard.
