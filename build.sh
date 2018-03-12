#!/usr/bin/env bash

AWS_DIR=$(mktemp -d /tmp/candutuft.aws.XXXXXXXXX)

python3 setup.py bdist_wheel --universal
cp ./dist/candytuft-*.whl ${AWS_DIR}
cp ./aws/* ${AWS_DIR}

zip -r -j ./aws.zip ${AWS_DIR}

rm -rf ./build
rm -rf ./dist
rm -rf ./*.egg-info

rm -rf ${AWS_DIR}
