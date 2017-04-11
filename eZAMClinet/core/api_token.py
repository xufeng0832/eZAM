#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Created by xuchao on 2017/2/15.

import hashlib, time


def get_token(username, token_id):
    """

    :param username: 用户名
    :param token_id:
    :return: md5加密后6位+时间戳
    """
    timestamp = int(time.time())
    md5_format_str = "%s\n%s\n%s" % (username, timestamp, token_id)
    obj = hashlib.md5()
    obj.update(md5_format_str.encode("utf8"))
    return obj.hexdigest()[11:17], timestamp


if __name__ == '__main__':
    print(get_token('alex', 'test'))


