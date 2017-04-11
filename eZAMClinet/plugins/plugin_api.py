#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Created by xuchao on 2017/2/14.

def LinuxSysInfo():
    from plugins.linux import sysinfo
    # print __file__
    return sysinfo.collect()


def WindowsSysInfo():
    from plugins.windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()
