#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys

if sys.version_info < (3, 0):
    raise RuntimeError('You need python 3 for this module.')

__author__ = "Isis Lovecruft, Georgy Angelov"
__date__ = "19 Jun 2013"
__version__ = (0, 2, 0)
__license__ = "MIT"

import collections
import hashlib

__all__ = ['hashlib']
