#!/usr/bin/env python3
# Created by xuchao on 2017/3/8.
from rest_framework import viewsets
from assets import models

from assets import rest_searializer


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = rest_searializer.UserSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = rest_searializer.AssetSerializer


class BusinessUnitViewSet(viewsets.ModelViewSet):
    queryset = models.BusinessUnit.objects.all()
    serializer_class = rest_searializer.BusinessUnitSerializer


class ManufactoryViewSet(viewsets.ModelViewSet):
    queryset = models.Manufactory.objects.all()
    serializer_class = rest_searializer.ManufactorySerializer


class ContractViewSet(viewsets.ModelViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = rest_searializer.ContractSerializer
