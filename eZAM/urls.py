"""eZAM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from assets import urls as api
from assets import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^asset_report_asset/',include(asset_urls)),
    url(r'^asset/',views.AssetListView),
    url(r'^assets$', views.AssetJsonView),
    url(r'^api/',include(api)),
    url(r'^test_api/',include('assets.rest_urls')),
    url(r'^api_test/',views.api_test),
    url('^index$',views.index),
    url('^cmdb$',views.CmdbView),

    url(r'^add-asset$', views.AddAssetView),
    url(r'^asset-(?P<asset_type>\w+)-(?P<asset_nid>\d+)$', views.AssetDetailView),

    url(r'^users$',views.UserListView),
    url(r'^user$',views.UserJsonView),

    url(r'^chart-(?P<chart_type>\w+)$',views.ChartView),
    ]
