#!/usr/bin/env bash

SCRIPT=`pwd`/$0
PATHNAME=`dirname $SCRIPT`
ROOT=$PATHNAME/..


echo "# this file is generated with scripts/pipFreeze.sh, do not update in any other way" > .requirements.txt
pip freeze >> .requirements.txt
cp .requirements.txt $ROOT/requirements.txt
cp .requirements.txt $ROOT/pyspark/requirements.txt
cp .requirements.txt $ROOT/src/requirements.txt
rm .requirements.txt
