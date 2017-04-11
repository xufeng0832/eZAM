#!/usr/bin/env python3
# Created by xuchao on 2017/3/7.
# from django.conf import settings
# from django.core.cache import cache
import json
import redis

# import datetime
r = redis.StrictRedis(host='192.168.56.2', port='6379', db=0)


# read cache user id
def read_from_cache(time, md5):
    key = '%s%s' % (time, md5)
    value = r.get(key)
    if value == None:
        data = None
    else:
        data = json.loads(value)
    return data


# write cache user id
def write_to_cache(time, md5):
    key = '%s%s' % (time, md5)
    print(key)
    r.set(key, 1, ex=300)
