#!/usr/bin/python
# -*- coding: utf-8 -*-
"""TeNOR Dummy and Internal ID module ..."""

import random

class TenorDummyId(object):
    """Manages mixed ids ... ints for vnfs and unicode for nsd"""
    def __init__(self, value):
        self._id = value

    def __add__(self, other):
        if type(self._id) is int:
            return str(self._id+random.randint(10,50))
        elif type(self._id) is unicode:
            number = int(self._id)
            return str(number+random.randint(10,50)).decode('unicode-escape')

    def __repr__(self):
        return str(self._id)
