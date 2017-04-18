#!/usr/bin/env python3
# _*_coding:utf-8_*_
# Created by xuchao on 2017/2/17.
import json, time, hashlib
from django.core.exceptions import ObjectDoesNotExist
from assets import models
from django.utils import timezone
from assets import redis_operation
import copy


class Asset(object):
    def __init__(self, request):
        self.request = request
        self.mandatory_fields = ['sn', 'asset_id', 'asset_type']  # 必须包含'sn','asset_id' and 'asset_type'
        self.field_sets = {
            'asset': ['manufactory'],
            'server': ['model', 'cpu_count', 'cpu_core_count', 'cpu_model', 'raid_type', 'os_type', 'os_distribution',
                       'os_release'],
            'networkdevice': []
        }
        # 定义返回错误信息
        self.response = {
            'error': [],
            'info': [],
            'warning': []
        }

    def response_msg(self, msg_type, key, msg):
        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    # 检查数据合法性,是否符合
    def mandatory_check(self, data, only_check_sn=False):
        for field in self.mandatory_fields:  # 检查数据必备字段['sn', 'asset_id', 'asset_type']
            if field not in data:
                self.response_msg('error', 'MandatoryCheckFailed',
                                  "The field [%s] is mandatory and not provided in your reporting data" % field)
        else:
            if self.response['error']: return False  # 如果有错误返回错误信息
        try:
            if not only_check_sn:  # False
                self.asset_obj = models.Asset.objects.get(id=int(data['asset_id']), sn=data['sn'])
            else:  # True
                self.asset_obj = models.Asset.objects.get(sn=data['sn'])
            return True

        except ObjectDoesNotExist as e:
            self.response_msg('error', 'AssetDataInvalid',
                              "Cannot find asset object in DB by using asset id [%s] and SN [%s] " % (
                                  data['asset_id'], data['sn']))
            self.waiting_approval = True  # 设置这条资产为等待批准
            return False

    def clinet_check(self, user, token_id, timestamp):
        """
        客户端合法性验证
        :param username: 用户名
        :param token_id:
        :return: md5加密后6位+时间戳
        """
        try:
            token = models.UserProfile.objects.get(email=user).token
            now_time = int(time.time())
            print(now_time,timestamp)
            if now_time - int(timestamp) > 300:
                return False
            md5_format_str = "%s\n%s\n%s" % (user, timestamp, token)
            obj = hashlib.md5()
            obj.update(md5_format_str.encode("utf8"))
            landing = redis_operation.read_from_cache(timestamp,user)
            # print(obj.hexdigest()[11:17],token_id)
            if obj.hexdigest()[11:17] == token_id and not landing:
                redis_operation.write_to_cache(timestamp,user)
                return True
        except Exception as e:
            return False

    def get_asset_id_by_sn(self):
        """当客户第一次报告的数据服务器,它不知道它的资产id,因此它将服务器要求的资产,然后再次报告数据"""
        data = self.request.POST.get("asset_data")  # 获取资产信息
        user = self.request.GET.get('user')
        timestamp = self.request.GET.get('timestamp')
        token = self.request.GET.get('token')
        rest = self.clinet_check(user=user, token_id=token, timestamp=timestamp)
        print(rest)
        if not rest:
            self.response_msg('error', 'AssetDataInvalid', "客户端是不合法的")
            response = self.response
            return response
        if data:
            try:
                data = json.loads(data)
                if self.mandatory_check(data, only_check_sn=True):  # 资产已经存在于数据库中,只是把它的资产id返回给客户机
                    response = {'asset_id': self.asset_obj.id}
                else:
                    if hasattr(self, 'waiting_approval'):  # 是否为待批准资产
                        self.response = {
                            'needs_aproval': "这是一个新的资产,需要管理员的批准创建新的资产id。"}
                        self.clean_data = data
                        self.save_new_asset_to_approval_zone()  # 在待批准区创建数据
            except Exception as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "报告的资产数据是无效或提供错误的数据")
        response = self.response
        return response

    def sorting_dic(self, c):
        dic1 = copy.deepcopy(c)
        return sorted(dic1.items(), key=lambda d: d[0])

    def loop_dic(self, dd):
        dd_dic = copy.deepcopy(dd)
        u = self.sorting_dic(dd_dic)
        for n, i in enumerate(u):
            if type(i[1]) is list:
                if i[1]:
                    for s, c in enumerate(i[1]):
                        if type(c) is dict:
                            u[n][1][s] = (self.sorting_dic(c))
                            u[n][1][s].sort()
                    i[1].sort()
        return u

    def save_new_asset_to_approval_zone(self):
        """
        当发现这是一个新的资产,将保存数据到批准区等待管理员批准
        :return:
        """
        asset_sn = self.clean_data.get('sn')
        clean_data = self.clean_data
        asset_already_in_approval_zone = models.NewAssetApprovalZone.objects.filter(sn=asset_sn)
        if asset_already_in_approval_zone:
            a = self.loop_dic(json.loads(asset_already_in_approval_zone.values('data')[0]['data']))
            b = self.loop_dic(clean_data)
            if a != b:
                asset_already_in_approval_zone.update(
                        data=json.dumps(self.clean_data),
                        manufactory=self.clean_data.get('manufactory'),
                        model=self.clean_data.get('model'),
                        asset_type=self.clean_data.get('asset_type'),
                        ram_size=self.clean_data.get('ram_size'),
                        cpu_model=self.clean_data.get('cpu_model'),
                        cpu_count=self.clean_data.get('cpu_count'),
                        cpu_core_count=self.clean_data.get('cpu_core_count'),
                        os_distribution=self.clean_data.get('os_distribution'),
                        os_release=self.clean_data.get('os_release'),
                        os_type=self.clean_data.get('os_type'),
                )
                # asset_already_in_approval_zone.save()
                self.response['needs_aproval'] = "该资产已更新(目前还在待批准区)"
            else:
                self.response['needs_aproval'] = "该资产已在待存区待批准,如无变动请勿重复提交"
        else:
            models.NewAssetApprovalZone.objects.get_or_create(  # 有则获取无则创建
                    sn=asset_sn,
                    data=json.dumps(self.clean_data),
                    manufactory=self.clean_data.get('manufactory'),
                    model=self.clean_data.get('model'),
                    asset_type=self.clean_data.get('asset_type'),
                    ram_size=self.clean_data.get('ram_size'),
                    cpu_model=self.clean_data.get('cpu_model'),
                    cpu_count=self.clean_data.get('cpu_count'),
                    cpu_core_count=self.clean_data.get('cpu_core_count'),
                    os_distribution=self.clean_data.get('os_distribution'),
                    os_release=self.clean_data.get('os_release'),
                    os_type=self.clean_data.get('os_type'), )
        return True

    # 检查数据完整性
    def data_is_valid(self):
        data = self.request.POST.get("asset_data")
        if data:
            try:
                data = json.loads(data)
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response['error']:
                    return True
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "The reported asset data is not valid or provided")

    def __is_new_asset(self):
        if not hasattr(self.asset_obj, self.clean_data['asset_type']):  # 新资产没有资产类型
            return True
        else:
            return False

    def data_inject(self):
        """将数据保存到数据库,data_is_valid()调用这个函数之前,必须返回True"""
        if self.__is_new_asset():
            # print('\033[32;1m---new asset,going to create----\033[0m')
            self.create_asset()
        else:  # asset already already exist , just update it
            # print('\033[33;1m---asset already exist ,going to update----\033[0m')

            self.update_asset()

    def data_is_valid_without_id(self):
        """当没有该资产时创建资产ID"""

        data = self.request.POST.get("asset_data")  # 获得需入库的QuerySet
        if data:
            try:
                data = json.loads(data)
                asset_obj = models.Asset.objects.get_or_create(sn=data.get('sn'), name=data.get(
                        'sn'))  # 查看该资产是否存在,无则创建
                data['asset_id'] = asset_obj[0].id  # 得到资产ID
                self.mandatory_check(data)
                self.clean_data = data
                if not self.response['error']:
                    return True
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        else:
            self.response_msg('error', 'AssetDataInvalid', "The reported asset data is not valid or provided")

    def reformat_components(self, identify_field, data_set):
        for k, data in data_set.items():
            data[identify_field] = k

    def __verify_field(self, data_set, field_key, data_type, required=True):
        """
        self.__verify_field(self.clean_data, 'model', str)
        :param data_set: 汇报的数据
        :param field_key: 必须字段
        :param data_type: 数据类型
        :param required:
        :return:
        """

        field_val = data_set.get(field_key)
        if field_val is not None:  # dict['model'] != None
            try:
                data_set[field_key] = data_type(field_val)  # str()
            except ValueError as e:
                self.response_msg('error', 'InvalidField',
                                  "[ %s ]字段的数据类型是无效的,正确的数据类型应该[ %s ]" % (
                                      field_key, data_type))

        elif required == True:
            self.response_msg('error', 'LackOfField',
                              "提供的字段[ %s ]没有值在你报告数据[ %s ]" % (
                                  field_key, data_set))

    def create_asset(self):
        """
        根据它的资产类型调用资产创建函数
        :return:
        """
        func = getattr(self, '_create_%s' % self.clean_data['asset_type'])  # _create_server
        func()

    def update_asset(self):
        func = getattr(self, '_update_%s' % self.clean_data['asset_type'])
        func()

    def _update_server(self):
        self.__update_asset_component(data_source=self.clean_data['nic'],
                                      fk='nic_set',
                                      update_fields=['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask','bonding'],
                                      identify_field='macaddress')
        self.__update_asset_component(data_source=self.clean_data['physical_disk_driver'],
                                      fk='disk_set',
                                      update_fields=['slot', 'sn', 'model', 'manufactory', 'capacity','iface_type'],
                                      identify_field='slot')
        self.__update_asset_component(data_source=self.clean_data['ram'],
                                      fk='ram_set',
                                      update_fields=['slot', 'sn', 'model', 'capacity'],
                                      identify_field='slot')
        self.__update_cpu_component()
        self.__update_manufactory_component()
        self.__update_server_component()

    def _create_server(self):
        self.__create_server_info()  #
        self.__create_or_update_manufactory()
        self.__create_cpu_component()
        self.__create_nic_component()
        self.__create_ram_component()
        self.__create_disk_component()

        log_msg = "Asset [<a href='/admin/assets/asset/%s/' target='_blank'>%s</a>] has been created!" % (
            self.asset_obj.id, self.asset_obj)
        self.response_msg('info', 'NewAssetOnline', log_msg)

    def __create_server_info(self, ignore_errs=False):
        """
        创建服务器信息
        :param ignore_errs: 是否忽略错误
        :return:
        """
        try:
            self.__verify_field(self.clean_data, 'model', str)
            # self.__verify_field(self.clean_data,'test_key',str)
            if not len(self.response['error']) or ignore_errs == True:  # 没有处理的时候或没有错误发生
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'raid_type': self.clean_data.get('raid_type'),
                    'model': self.clean_data.get('model'),
                    'os_type': self.clean_data.get('os_type'),
                    'os_distribution': self.clean_data.get('os_distribution'),
                    'os_release': self.clean_data.get('os_release'),
                }

                obj = models.Server(**data_set)
                obj.save()
                return obj
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [server] %s' % str(e))

    def __create_or_update_manufactory(self, ignore_errs=False):
        """
        创建制造
        :param ignore_errs:
        :return:
        """
        try:
            self.__verify_field(self.clean_data, 'manufactory', str)
            manufactory = self.clean_data.get('manufactory')
            if not len(self.response['error']) or ignore_errs == True:  # 没有处理的时候或没有错误发生
                obj_exist = models.Manufactory.objects.filter(manufactory=manufactory)
                if obj_exist:  # 如果制造商不存在则创建
                    obj = obj_exist[0]
                else:  # create a new one
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                self.asset_obj.manufactory = obj
                self.asset_obj.save()
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [manufactory] %s' % str(e))

    def __create_cpu_component(self, ignore_errs=False):
        """
        创建CPU信息
        :param ignore_errs:
        :return:
        """
        try:
            self.__verify_field(self.clean_data, 'model', str)
            self.__verify_field(self.clean_data, 'cpu_count', int)
            self.__verify_field(self.clean_data, 'cpu_core_count', int)
            if not len(self.response['error']) or ignore_errs == True:  # 没有处理的时候或没有错误发生
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'cpu_model': self.clean_data.get('cpu_model'),
                    'cpu_count': self.clean_data.get('cpu_count'),
                    'cpu_core_count': self.clean_data.get('cpu_core_count'),
                }

                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" % (self.asset_obj, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
                return obj
        except Exception as e:
            self.response_msg('error', 'ObjectCreationException', 'Object [cpu] %s' % str(e))

    def __create_disk_component(self):
        """
        创建硬盘信息
        :return:
        """
        disk_info = self.clean_data.get('physical_disk_driver')
        if disk_info:
            for disk_item in disk_info:
                try:
                    self.__verify_field(disk_item, 'slot', str)
                    self.__verify_field(disk_item, 'capacity', float)
                    self.__verify_field(disk_item, 'iface_type', str)
                    self.__verify_field(disk_item, 'model', str)
                    if not len(self.response['error']):  # 没有处理的时候或没有错误发生
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'sn': disk_item.get('sn'),
                            'slot': disk_item.get('slot'),
                            'capacity': disk_item.get('capacity'),
                            'model': disk_item.get('model'),
                            'iface_type': disk_item.get('iface_type'),
                            'manufactory': disk_item.get('manufactory'),
                        }

                        obj = models.Disk(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [disk] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'Disk info is not provied in your reporting data')

    def __create_nic_component(self):
        """
        创建网卡信息
        :return:
        """
        nic_info = self.clean_data.get('nic')
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item, 'macaddress', str)
                    if not len(self.response['error']):  # 没有处理的时候或没有错误发生
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'name': nic_item.get('name'),
                            'sn': nic_item.get('sn'),
                            'macaddress': nic_item.get('macaddress'),
                            'ipaddress': nic_item.get('ipaddress'),
                            'bonding': nic_item.get('bonding'),
                            'model': nic_item.get('model'),
                            'netmask': nic_item.get('netmask'),
                        }

                        obj = models.NIC(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [nic] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'NIC info is not provied in your reporting data')

    def __create_ram_component(self):
        """
        创建内存信息
        :return:
        """
        ram_info = self.clean_data.get('ram')
        if ram_info:
            for ram_item in ram_info:
                try:
                    self.__verify_field(ram_item, 'capacity', int)
                    if not len(self.response['error']):  # 没有处理的时候或没有错误发生
                        data_set = {
                            'asset_id': self.asset_obj.id,
                            'slot': ram_item.get("slot"),
                            'sn': ram_item.get('sn'),
                            'capacity': ram_item.get('capacity'),
                            'model': ram_item.get('model'),
                        }

                        obj = models.RAM(**data_set)
                        obj.save()

                except Exception as e:
                    self.response_msg('error', 'ObjectCreationException', 'Object [ram] %s' % str(e))
        else:
            self.response_msg('error', 'LackOfData', 'RAM info is not provied in your reporting data')

    def __update_server_component(self):
        update_fields = ['model', 'raid_type', 'os_type', 'os_distribution', 'os_release']
        if hasattr(self.asset_obj, 'server'):
            self.__compare_componet(model_obj=self.asset_obj.server,
                                    fields_from_db=update_fields,
                                    data_source=self.clean_data)
        else:
            self.__create_server_info(ignore_errs=True)

    def __update_manufactory_component(self):
        self.__create_or_update_manufactory(ignore_errs=True)

    def __update_cpu_component(self):
        update_fields = ['cpu_model', 'cpu_count', 'cpu_core_count']  # 必填字段
        if hasattr(self.asset_obj, 'cpu'):
            self.__compare_componet(model_obj=self.asset_obj.cpu,
                                    fields_from_db=update_fields,
                                    data_source=self.clean_data)
        else:
            self.__create_cpu_component(ignore_errs=True)

    def __update_asset_component(self, data_source, fk, update_fields, identify_field=None):
        """

        :param data_source: dict or list (request.POST)
        :param fk:跨表查询
        :param update_fields:更新字段 list
        :param identify_field: 唯一性字段
        :return:
        """
        # print(data_source, update_fields, identify_field,fk)
        try:
            # models.Asset.objects.get(id=int(data['asset_id']), sn=data['sn'])
            component_obj = getattr(self.asset_obj, fk)  # 反向查询该server的nic
            if hasattr(component_obj, 'select_related'):
                objects_from_db = component_obj.select_related()  # 把数据取出来从数据库
                for obj in objects_from_db:  # ['08:00:27:01:f3:df', '08:00:27:28:7e:4d']
                    key_field_data = getattr(obj, identify_field)  # 获取唯一性的数据
                    # 使用这个key_field_data找到相关数据来源报告数据
                    if type(data_source) is list:
                        for source_data_item in data_source:
                            key_field_data_from_source_data = source_data_item.get(
                                    identify_field)  # client_data.get('macaddress'),'08:00:27:01:f3:df'
                            if key_field_data_from_source_data:  # 匹配上了对应的网卡
                                # 数据库的macaddress = 新数据macaddress
                                if key_field_data == key_field_data_from_source_data:  # 找到匹配的源数据进行匹配更新
                                    self.__compare_componet(model_obj=obj, fields_from_db=update_fields,
                                                            data_source=source_data_item)
                                    # print('------matched.->', key_field_data, key_field_data_from_source_data)
                                    break
                            else:  # key field data from source data cannot be none
                                self.response_msg('warning', 'AssetUpdateWarning',
                                                  "Asset component [%s]'s key field [%s] is not provided in reporting data " % (
                                                      fk, identify_field))

                        else:  # 找不到任何匹配
                            self.response_msg("error", "AssetUpdateWarning",
                                              "Cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!" % (
                                                  key_field_data))
                    elif type(data_source) is dict:
                        for key, source_data_item in data_source.items():
                            key_field_data_from_source_data = source_data_item.get(identify_field)
                            if key_field_data_from_source_data:
                                if key_field_data == key_field_data_from_source_data:  # 找到匹配的源数据进行匹配更新
                                    self.__compare_componet(model_obj=obj, fields_from_db=update_fields,
                                                            data_source=source_data_item)
                                    break
                            else:
                                self.response_msg('warning', 'AssetUpdateWarning',
                                                  "Asset component [%s]'s key field [%s] is not provided in reporting data " % (
                                                      fk, identify_field))

                        else:
                            pass
                            # print(
                            #         '\033[33;1mWarning:cannot find any matches in source data by using key field val [%s],component data is missing in reporting data!\033[0m' % (
                            #             key_field_data))
                    else:
                        # print('\033[31;1mMust be sth wrong,logic should goes to here at all.\033[0m')
                        pass
                # 比较数据库的所有字段和报告数据的数据源 models.Asset.objects.last().nic_set
                self.__filter_add_or_deleted_components(model_obj_name=component_obj.model._meta.object_name,
                                                        data_from_db=objects_from_db,
                                                        data_source=data_source,
                                                        identify_field=identify_field)

            else:  # this component is reverse fk relation with Asset model
                pass
        except ValueError as e:
            # print('\033[41;1m%s\033[0m' % str(e))
            pass

    def __filter_add_or_deleted_components(self, model_obj_name, data_from_db, data_source, identify_field):
        """
           DB          New
        [1,2,3]      [2,3,4]
        这个函数是过滤掉所有新数据在数据库中不存在的数据, 数据库中存在,新数据不存在
        :param model_obj_name: 表名
        :param data_from_db: 表数据
        :param data_source: 新数据 dict or list
        :param identify_field:  唯一性字段
        :return:
        """
        # print(data_from_db, data_source, identify_field)
        data_source_key_list = []  # 从客户端数据保存所有必备字段 [macaddress1,macaddress2]
        if type(data_source) is list:
            for data in data_source:
                data_source_key_list.append(data.get(identify_field))
        # 新数据{'2', '3', '4'}
        data_source_key_list = set(data_source_key_list)  # {'08:00:27:28:7e:4d', '08:00:27:01:f3:df'}
        # 数据库数据 {'1','2','3')
        data_identify_val_from_db = set([getattr(obj, identify_field) for obj in data_from_db])

        data_only_in_db = data_identify_val_from_db - data_source_key_list  # 数据库中多余的
        data_only_in_data_source = data_source_key_list - data_identify_val_from_db  # 数据库中没有的
        self.__delete_components(all_components=data_from_db, delete_list=data_only_in_db,
                                 identify_field=identify_field)
        if data_only_in_data_source:
            self.__add_components(model_obj_name=model_obj_name, all_components=data_source,
                                  add_list=data_only_in_data_source, identify_field=identify_field)

    def __add_components(self, model_obj_name, all_components, add_list, identify_field):
        """

        :param model_obj_name:  表名
        :param all_components:  新数据
        :param add_list:  没有的数据
        :param identify_field:  唯一性字段
        :return:
        """
        model_class = getattr(models, model_obj_name)
        will_be_creating_list = []
        for data in all_components:
            if data[identify_field] in add_list:
                will_be_creating_list.append(data)

        try:
            for component in will_be_creating_list:
                data_set = {}
                # ['name', 'sn', 'model', 'macaddress', 'ipaddress', 'netmask', 'bonding']
                for field in model_class.auto_create_fields:
                    data_set[field] = component.get(field)
                data_set['asset_id'] = self.asset_obj.id
                obj = model_class(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> component[%s] has justed added a new item [%s]" % (
                    self.asset_obj, model_obj_name, data_set)
                self.response_msg('info', 'NewComponentAdded', log_msg)
                log_handler(self.asset_obj, 'NewComponentAdded', self.request.user, log_msg, model_obj_name)

        except Exception as e:
            log_msg = "Asset[%s] --> component[%s] has error: %s" % (self.asset_obj, model_obj_name, str(e))
            self.response_msg('error', "AddingComponentException", log_msg)

    def __delete_components(self, all_components, delete_list, identify_field):
        """

        :param all_components:  表数据
        :param delete_list: 多余数据
        :param identify_field:  唯一性字段
        :return:
        """
        deleting_obj_list = []
        # print('--deleting components', delete_list, identify_field)
        for obj in all_components:  # [nic1_obj, nic2_obj,....]
            val = getattr(obj, identify_field)
            if val in delete_list:
                deleting_obj_list.append(obj)

        for i in deleting_obj_list:
            log_msg = "Asset[%s] --> component[%s] --> is lacking from reporting source data, assume it has been removed or replaced,will also delete it from DB" % (
                self.asset_obj, i)
            self.response_msg('info', 'HardwareChanges', log_msg)
            log_handler(self.asset_obj, 'HardwareChanges', self.request.user, log_msg, i)
            i.delete()

    def __compare_componet(self, model_obj, fields_from_db, data_source):
        """

        :param model_obj: 现在资产数据;queryset
        :param fields_from_db: 必填字段
        :param data_source: 新数据
        :return:
        """
        # print('---going to compare:[%s]' % model_obj, fields_from_db)
        # print('---source data:', data_source)
        for field in fields_from_db:
            val_from_db = getattr(model_obj, field)  # 数据库的数据
            val_from_data_source = data_source.get(field)  # queryset的数据
            if val_from_data_source:
                if type(val_from_db) is int:
                    val_from_data_source = int(val_from_data_source)
                elif type(val_from_db) is float:
                    val_from_data_source = float(val_from_data_source)
                elif type(val_from_db) is str:
                    val_from_data_source = str(val_from_data_source).strip()
                if val_from_db == val_from_data_source:  # this field haven't changed since last update
                    pass
                else:
                    db_field = model_obj._meta.get_field(field)  # 获得该数据的语句
                    db_field.save_form_data(model_obj, val_from_data_source)  # 更新数据
                    model_obj.update_date = timezone.now()  # 修改:更新时间
                    model_obj.save()
                    log_msg = "Asset[%s] --> component[%s] --> field[%s] has changed from [%s] to [%s]" % (
                        self.asset_obj, model_obj, field, val_from_db, val_from_data_source)
                    self.response_msg('info', 'FieldChanged', log_msg)
                    log_handler(self.asset_obj, 'FieldChanged', self.request.user, log_msg, model_obj)
            else:
                self.response_msg('warning', 'AssetUpdateWarning',
                                  "Asset component [%s]'s field [%s] is not provided in reporting data " % (
                                      model_obj, field))

        # model_obj.save()


def log_handler(asset_obj, event_name, user, detail, component=None):
    '''    (1,u'硬件变更'),
        (2,u'新增配件'),
        (3,u'设备下线'),
        (4,u'设备上线'),'''
    log_catelog = {
        1: ['FieldChanged', 'HardwareChanges'],
        2: ['NewComponentAdded'],
    }
    if not user.id:
        user = models.UserProfile.objects.filter(is_superuser=True).last()
    event_type = None
    for k, v in log_catelog.items():
        if event_name in v:
            event_type = k
            break
    log_obj = models.EventLog(
            name=event_name,
            event_type=event_type,
            asset_id=asset_obj.id,
            component=component,
            detail=detail,
            user_id=user.id
    )

    log_obj.save()
