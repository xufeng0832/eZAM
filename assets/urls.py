#!/usr/bin/env python3
# Created by xuchao on 2017/2/17.

from django.conf.urls import url
from assets import views

urlpatterns = [
    # 正式资产
    url(r'asset/report/$', views.asset_report, name='asset_report'),
    # 新资产
    url(r'asset/report/asset_with_no_asset_id/$', views.asset_with_no_asset_id, name='acquire_asset_id'),
    # 批准新资产入正式资产
    url(r'asset/new_assets/approval/$', views.new_assets_approval, name="new_assets_approval"),

]
