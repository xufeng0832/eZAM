#!/usr/bin/env python3
# Created by xuchao on 2017/3/8.

class BaseResponse(object):
    def __init__(self):
        self.status = True
        self.message = None
        self.data = None
        self.error = None
