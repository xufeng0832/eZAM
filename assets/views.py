from django.shortcuts import render
from django.http import HttpResponse
import json
from assets import core
from django.views.decorators.csrf import csrf_exempt
from assets import models
from assets import rest_searializer
from web.service import chart, user
from django.http import JsonResponse
from assets.service import asset


# Create your views here.


@csrf_exempt
def asset_with_no_asset_id(request):  # 新资产进入待批准库
    if request.method == 'POST':
        # print(request.POST.get("asset_data"))
        ass_handler = core.Asset(request)
        res = ass_handler.get_asset_id_by_sn()

        # return render(request,'assets/acquire_asset_id_test.html',{'response':res})
        # print('---------:20')
        return HttpResponse(json.dumps(res))


# 新资产批准入口
def new_assets_approval(request):
    if request.method == 'POST':

        request.POST = request.POST.copy()  # 以备修改发来的数据

        approved_asset_list = request.POST.getlist('approved_asset_list')  # 获取提交过来的IdList
        # 获取该IdList的QuerySet
        approved_asset_list = models.NewAssetApprovalZone.objects.filter(id__in=approved_asset_list)

        response_dic = {}
        for obj in approved_asset_list:
            # 待批准数据
            request.POST['asset_data'] = obj.data
            ass_handler = core.Asset(request)
            if ass_handler.data_is_valid_without_id():  # 查看该资产是否存在,无则创建
                ass_handler.data_inject()
                obj.approved = True
                obj.save()

            response_dic[obj.id] = ass_handler.response
        return render(request, 'assets/new_assets_approval.html',
                      {'new_assets': approved_asset_list, 'response_dic': response_dic})
    else:
        ids = request.GET.get('ids')
        id_list = ids.split(',')
        new_assets = models.NewAssetApprovalZone.objects.filter(id__in=id_list)
        return render(request, 'assets/new_assets_approval.html', {'new_assets': new_assets})


@csrf_exempt
def asset_report(request):
    # print(request.GET)
    if request.method == 'POST':
        ass_handler = core.Asset(request)
        if ass_handler.data_is_valid():
            # print("----asset data valid:")
            ass_handler.data_inject()
            # return HttpResponse(json.dumps(ass_handler.response))

        return HttpResponse(json.dumps(ass_handler.response))
        # return render(request,'assets/asset_report_test.html',{'response':ass_handler.response})
        # else:
        # return HttpResponse(json.dumps(ass_handler.response))

    return HttpResponse('--test--')


def api_test(request):
    if request.method == "GET":
        return render(request, "test_post.html")

    else:
        data = json.loads(request.POST.get("data"))
        print("--->", data)

        rest_obj = rest_searializer.AssetSerializer(data=data, many=True)  # many 可以创建多个 '[{},{}]'
        if rest_obj.is_valid():
            rest_obj.save()

        return render(request, "test_post.html", {"errors": rest_obj.errors, "data": rest_obj.data})


# class IndexView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'index.html')


def index(request):
    if request.method == 'GET':
        print(request.META.get('PATH_INFO'))
        return render(request, 'index.html')


def CmdbView(request):
    if request.method == 'GET':
        return render(request, 'cmdb.html')


def AssetListView(request):
    if request.method == 'GET':
        return render(request, 'asset_list.html')


def AssetJsonView(request):
    if request.method == 'GET':
        obj = asset.Asset()
        response = obj.fetch_assets(request)
        return JsonResponse(response.__dict__)

    if request.method == 'DELETE':
        response = asset.Asset.delete_assets(request)
        return JsonResponse(response.__dict__)

    if request.method == 'PUT':
        response = asset.Asset.put_assets(request)
        return JsonResponse(response.__dict__)


def ChartView(request, chart_type):
    if chart_type == 'business':
        response = chart.Business.chart()
        # print(request.META)
    if chart_type == 'dynamic':
        last_id = request.GET.get('last_id')
        response = chart.Dynamic.chart(last_id)
    return JsonResponse(response.__dict__, safe=False, json_dumps_params={'ensure_ascii': False})


def UserListView(request):
    if request.method == 'GET':
        return render(request, 'users_list.html')


def UserJsonView(request):
    if request.method == 'GET':
        obj = user.User()
        response = obj.fetch_users(request)
        return JsonResponse(response.__dict__)

    if request.method == 'DELETE':
        response = user.User.delete_users(request)
        return JsonResponse(response.__dict__)

    if request.method == 'PUT':
        response = user.User.put_users(request)
        return JsonResponse(response.__dict__)


def AssetDetailView(request, asset_type, asset_nid):
    response = asset.Asset.assets_detail(asset_type, asset_nid)
    # print(request.data.name)
    return render(request, 'asset_detail.html', {'response': response, 'device_type_id': asset_type})


def AddAssetView(request):
    if request.method == 'GET':
        return render(request, 'add_asset.html')
