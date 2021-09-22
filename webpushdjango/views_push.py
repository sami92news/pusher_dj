import json

from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from pywebpush import webpush
from webpush.models import SubscriptionInfo

from webpush.utils import _process_subscription_info

from webpush import send_user_notification


@require_GET
def home(request):
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
    print(type(vapid_key))
    user = request.user
    return render(request, 'home.html', {user: user, 'vapid_key': vapid_key})


def send_to_top(request):
    _send_notification()
    return JsonResponse(status=200, data={"message": "Web push sent"})


def _send_notification():
    subscription_data, vapid_data, push_data = prepare_note()
    payload = json.dumps(push_data)
    req = webpush(subscription_info=subscription_data, data=payload, ttl=1000, **vapid_data)
    return req


def prepare_note():
    obj = SubscriptionInfo.objects.first()

    subscription_data = {
        'endpoint': obj.endpoint,
        'auth': obj.auth,
        'p256dh': obj.p256dh
    }

    endpoint = subscription_data.get("endpoint")
    p256dh = subscription_data.get("p256dh")
    auth = subscription_data.get("auth")

    subscription_data = {
        "endpoint": endpoint,
        "keys": {"p256dh": p256dh, "auth": auth}
    }

    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_private_key = webpush_settings.get('VAPID_PRIVATE_KEY')
    vapid_admin_email = webpush_settings.get('VAPID_ADMIN_EMAIL')

    vapid_data = {
        'vapid_private_key': vapid_private_key,
        'vapid_claims': {"sub": "mailto:{}".format(vapid_admin_email)}
    }
    site_url = "https://92newshd.tv/"
    post_data = {
        'id': '6291524',
        'slug': 'ecb-cancels-tour-of-men-and-women-teams-to-pakistan',
        'title': 'ECB Cancels Tour Of Men And Women Teams To Pakistan',
        'feature_image': 'https://92newshd.tv/wp-content/uploads/2021/09/20161137_4.webp',
    }
    post_url = '{}about/{}/{}'.format(site_url, post_data['id'], post_data['slug'])
    push_data = {
        "head": "New article published at 92news",
        "body": post_data['title'],
        "icon": post_data['feature_image'],
        "url": post_url
    }
    return subscription_data, vapid_data, push_data


@require_POST
@csrf_exempt
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)

        if 'head' not in data and 'body' not in data and 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']

        user = get_object_or_404(User, pk=user_id)

        payload = {'head': data['head'], 'body': data['body']}
        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})

    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})
