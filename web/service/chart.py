#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created by xuchao on 2017/3/8.
from assets import models
from utils.response import BaseResponse


class Business(object):
    @staticmethod
    def chart():
        response = BaseResponse()
        try:
            sql = """
                SELECT
                    id,
                    name,
                    (select count(id) from assets_asset as A where B.id=A.business_unit_id and A.asset_type='server') as server_count,
                    (select count(id) from assets_asset as A where B.id=A.business_unit_id and A.asset_type='networkdevice') as networkdevice_count,
                    (select count(id) from assets_asset as A where B.id=A.business_unit_id and A.asset_type='storagedevice') as storagedevice_count,
                    (select count(id) from assets_asset as A where B.id=A.business_unit_id and A.asset_type='securitydevice') as securitydevice_count,
                    (select count(id) from assets_asset as A where B.id=A.business_unit_id and A.asset_type='software') as software_count
                from assets_businessunit as B"""
            result = models.BusinessUnit.objects.raw(sql)
            ret = {
                'categories': [],
                'series': [
                    {
                        "name": '服务器',
                        "data": []
                    },{
                        "name": '网络设备',
                        "data": []
                    }, {
                        "name": '存储设备',
                        "data": []
                    }, {
                        "name": '安全设备',
                        "data": []
                    }, {
                        "name": '软件资产',
                        "data": []
                    }
                ]
            }
            for row in result:
                ret['categories'].append(row.name)
                ret['series'][0]['data'].append(row.server_count)
                ret['series'][1]['data'].append(row.networkdevice_count)
                ret['series'][2]['data'].append(row.storagedevice_count)
                ret['series'][3]['data'].append(row.securitydevice_count)
                ret['series'][4]['data'].append(row.software_count)
            response.data = ret
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response


class Dynamic(object):
    @staticmethod
    def chart(last_id):

        response = BaseResponse()
        try:
            import time
            import random

            last_id = int(last_id)
            if last_id == 0:
                end = 100
            else:
                end = random.randint(1, 10)
            ret = []
            for i in range(0, end):
                temp = {'x': time.time() * 1000, 'y': random.randint(1, 1000)}
                ret.append(temp)
            last_id += 10
            response.data = ret
            response.last_id = last_id
        except Exception as e:
            response.status = False
            response.message = str(e)

        return response
