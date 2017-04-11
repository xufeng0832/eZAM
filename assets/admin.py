from django.contrib import admin
from  django.http import HttpResponseRedirect


# Register your models here.


class AssetAdmin(admin.ModelAdmin):
    list_display = ('sn', 'id', 'create_date')
    # 只对  多对多  有效
    filter_horizontal = ('tags',)


class EventLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'asset')


class NewAssetApprovalZoneAdmin(admin.ModelAdmin):
    # 显示表头
    list_display = ['sn', 'id', 'asset_type', 'manufactory', 'model', 'ram_size', 'cpu_model', 'date', 'approved',
                    'approved_by', 'approved_date']
    # 过滤(右侧)
    list_filter = ('asset_type', 'date')
    # 搜索(上方)
    search_fields = ('sn',)
    # 批量控制
    actions = ['approve_selected_rows', ]

    def approve_selected_rows(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/api/asset/new_assets/approval/?ids=%s" % (",".join(selected)))

    approve_selected_rows.short_description = "批准入库"


# Register your models here.
from assets import models

admin.site.register(models.Asset, AssetAdmin)
admin.site.register(models.BusinessUnit)
admin.site.register(models.IDC)
admin.site.register(models.Server)
admin.site.register(models.NetworkDevice)
admin.site.register(models.SecurityDevice)
admin.site.register(models.Disk)
admin.site.register(models.NIC)
admin.site.register(models.CPU)
admin.site.register(models.RAM)
admin.site.register(models.RaidAdaptor)
admin.site.register(models.Contract)
admin.site.register(models.UserProfile)
admin.site.register(models.EventLog)
admin.site.register(models.Manufactory)
admin.site.register(models.Tag)
admin.site.register(models.NewAssetApprovalZone, NewAssetApprovalZoneAdmin)
