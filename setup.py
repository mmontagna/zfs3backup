import os
from setuptools import setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))

VERSION = open(os.path.join(dir_path, 'VERSION')).read()


setup(
    name="zfs3backup",
    version=VERSION,
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=["boto3"],
    author="Marco Montagna",
    author_email="marcojoemontagna@gmail.com",
    url="https://github.com/mmontagna/zfs3backup",
    description="Backup ZFS snapshots to S3",
    entry_points={
        'console_scripts': [
            'pput = zfs3backup.pput:main',
            'zfs3backup = zfs3backup.snap:main',
            'zfs3backup_get = zfs3backup.get:main',
            'zfs3backup_ssh_sync = zfs3backup.ssh_sync:main'
        ]
    },
    keywords='ZFS backup',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
    ],
)
