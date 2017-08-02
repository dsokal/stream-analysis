#!/usr/bin/env sh

supervisor -e py -x python -- -u producers_manager.py
