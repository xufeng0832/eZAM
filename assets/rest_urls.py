#!/usr/bin/env python3
# Created by xuchao on 2017/3/8.
from rest_framework import routers
from django.conf.urls import url, include
from assets import rest_viewset

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', rest_viewset.UserViewSet)
router.register(r'assets', rest_viewset.AssetViewSet)
router.register(r'manufactory', rest_viewset.ManufactoryViewSet)
router.register(r'business_unit', rest_viewset.BusinessUnitViewSet)
router.register(r'Contract', rest_viewset.ContractViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
