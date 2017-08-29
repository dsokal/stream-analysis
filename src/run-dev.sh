#!/usr/bin/env sh

supervisor -e py -x python $1 -- -u -m $2
