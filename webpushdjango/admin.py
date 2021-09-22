from django.contrib import admin
from webpush.models import SubscriptionInfo


class SubscriptionInfoAdmin(admin.ModelAdmin):
    list_display = ['*']


admin.site.register(SubscriptionInfo, SubscriptionInfoAdmin)