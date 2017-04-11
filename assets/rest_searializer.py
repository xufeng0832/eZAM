#!/usr/bin/env python3
# Created by xuchao on 2017/3/8.

from django.conf.urls import url, include
from assets import models
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.

# 定义了一个表现形式
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ('name', 'token', 'email', 'is_staff')


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Asset
        fields = ('id', 'name', 'asset_type', 'business_unit', 'sn', 'manufactory', 'management_ip')
        depth = 2


class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessUnit
        fields = ('parent_unit', 'name', 'id')


# class ManufactorySerializer(serializers.HyperlinkedModelSerializer):
class ManufactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Manufactory
        fields = ('manufactory', 'id')

# ContractViewSet

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contract
        fields = ('sn', 'name', 'memo', 'price', 'detail', 'start_date', 'end_date', 'license_num')