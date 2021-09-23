from django.contrib import admin
from webpush.models import SubscriptionInfo


class SubscriptionInfoAdmin(admin.ModelAdmin):
    list_display = [
        'browser',
        'endpoint',
        'auth',
        'p256dh'
    ]


admin.site.register(SubscriptionInfo, SubscriptionInfoAdmin)