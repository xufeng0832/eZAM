#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Created by xuchao on 2017/2/14.

from core import info_collection
from conf import settings
import urllib.request, sys, os, json, datetime
import urllib.parse
from core import api_token


class ArgvHandler(object):
    def __init__(self, argv_list):
        self.argvs = argv_list
        self.parse_argv()

    def parse_argv(self):
        if len(self.argvs) > 1:
            if hasattr(self, self.argvs[1]):
                func = getattr(self, self.argvs[1])
                func()
            else:
                self.help_msg()
        else:
            self.help_msg()

    def help_msg(self):
        msg = '''
        collect_data   收集资产数据
        run_forever    未实现
        get_asset_id   获取资产id
        report_asset   汇报资产数据到服务器
        '''
        print(msg)

    def collect_data(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()  # 收集
        print(asset_data)

    def run_forever(self):
        pass

    def __attach_token(self, url_str):
        """在请求URL中加入 token_id和用户名 使用md5方式加密"""
        user = settings.Params['auth']['user']
        token_id = settings.Params['auth']['token']
        md5_token, timestamp = api_token.get_token(user, token_id)
        url_arg_str = "user=%s&timestamp=%s&token=%s" % (user, timestamp, md5_token)  # 拼接token
        if "?" in url_str:  # already has arg
            new_url = url_str + "&" + url_arg_str
        else:
            new_url = url_str + "?" + url_arg_str
        return new_url

    def __submit_data(self, action_type, data, method):
        '''
        发送数据到服务器
        :param action_type: url
        :param data: 具体要发送的数据
        :param method: get/post
        :return:
        '''
        if action_type in settings.Params['urls']:
            if type(settings.Params['port']) is int:
                # 拼接URL:192.168.0.151:80/asset/report/asset_with_no_asset_id/
                url = "http://%s:%s%s" % (
                    settings.Params['server'], settings.Params['port'], settings.Params['urls'][action_type])
            else:
                url = "http://%s%s" % (settings.Params['server'], settings.Params['urls'][action_type])

            url = self.__attach_token(url)  # 获得加密验证url
            # print('Connecting [%s], it may take a minute' % url)
            if method == "get":
                args = ""
                for k, v in data.items():
                    args += "&%s=%s" % (k, v)
                args = args[1:]
                url_with_args = "%s?%s" % (url, args)
                print(url_with_args)
                try:
                    req = urllib.request.urlopen(url_with_args, timeout=settings.Params['request_timeout'])
                    # req_data =urlopen(req,timeout=settings.Params['request_timeout'])
                    # callback = req_data.read()
                    callback = req.read()
                    print("-->server response:", callback)
                    return callback
                except urllib.URLError as e:
                    sys.exit("\033[31;1m%s\033[0m" % e)
            elif method == "post":
                try:
                    data_encode = urllib.parse.urlencode(data).encode()  # 格式化资产数据成URL的格式
                    req = urllib.request.urlopen(url=url, data=data_encode, timeout=settings.Params['request_timeout'])
                    callback = req.read()
                    callback = json.loads(callback.decode())
                    print("\033[31;1m[%s]:[%s]\033[0m response:\n%s" % (method, url, callback))
                    return callback  # 返回资产ID
                except Exception as e:
                    sys.exit("\033[31;1m%s\033[0m" % e)
        else:
            raise KeyError

    # def __get_asset_id_by_sn(self,sn):
    #    return  self.__submit_data("get_asset_id_by_sn",{"sn":sn},"get")
    def load_asset_id(self, sn=None):
        asset_id_file = settings.Params['asset_id']  # 获取资产ID存放文件位置
        if os.path.isfile(asset_id_file):  # 判断资产ID文件是否存在,如果存在返回ID
            asset_id = open(asset_id_file).read().strip()
            if asset_id.isdigit():
                return asset_id

    def __update_asset_id(self, new_asset_id):  # 添加或更新资产ID
        asset_id_file = settings.Params['asset_id']
        f = open(asset_id_file, "w", encoding="utf-8")
        f.write(str(new_asset_id))
        f.close()

    def report_asset(self):
        obj = info_collection.InfoCollection()
        asset_data = obj.collect()  # 收集到信息
        asset_id = self.load_asset_id(asset_data["sn"])  # 获取资产ID,(int/None)
        if asset_id:  # 判断提交地址
            asset_data["asset_id"] = asset_id
            post_url = "asset_report"
        else:  # 第一次提交
            '''报告到另一个url,这将把资产审批等待区,当资产被批准后,该请求的汇报资产的ID'''

            asset_data["asset_id"] = None
            post_url = "asset_report_with_no_id"

        data = {"asset_data": json.dumps(asset_data)}  # 封装数据
        response = self.__submit_data(post_url, data, method="post")

        if "asset_id" in response:  # 如果收到资产ID则更新
            self.__update_asset_id(response["asset_id"])

        self.log_record(response)

    def log_record(self, log, action_type=None):
        f = open(settings.Params["log_file"], "ab")
        if log is str:
            pass
        if type(log) is dict:

            if "info" in log:
                for msg in log["info"]:
                    log_format = "%s\tINFO\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format.encode())
            if "error" in log:
                for msg in log["error"]:
                    log_format = "%s\tERROR\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format.encode())
            if "warning" in log:
                for msg in log["warning"]:
                    log_format = "%s\tWARNING\t%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), msg)
                    f.write(log_format.encode())

        f.close()
