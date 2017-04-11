#!/usr/bin/env python3
#_*_coding:utf8_*_
# Created by xuchao on 2017/2/15.

import os
BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Params = {
    "server": "192.168.0.151",
    # "server": "127.0.0.1",
    "port":8000,
    'request_timeout':30,
    "urls":{
          "asset_report_with_no_id":"/api/asset/report/asset_with_no_asset_id/", #新资产待批准区
          "asset_report":"/api/asset/report/", #正式资产表接口
        },
    'asset_id': '%s/var/.asset_id' % BaseDir,
    'log_file': '%s/logs/run_log' % BaseDir,

    'auth':{
        'user':'xufeng0832@163.com',  # email
        'token': 'test'
        },
}
