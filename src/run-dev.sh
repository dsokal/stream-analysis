#!/usr/bin/env sh

supervisor -e py -x python -- -u -m $@
