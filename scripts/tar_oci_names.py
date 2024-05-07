#!/usr/bin/env python3

import tarfile
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description='Extracts the names of the images in an OCI tar archive (from docker save).')
    parser.add_argument('tarfile', help='The tar file to extract the image names from.')
    args = parser.parse_args()

    with tarfile.open(args.tarfile, 'r') as tar:
        for member in tar.getmembers():
            if member.name == 'manifest.json':
                with tar.extractfile(member) as f:
                    manifest = json.loads(f.read().decode('utf-8'))
                    for image in manifest:
                        for tag in image['RepoTags']:
                            print(tag)

if __name__ == '__main__':
    main()
