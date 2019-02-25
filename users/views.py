import requests

from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView


# Create your views here.
from mysite.exceptions import ServiceUnavailable
from users.constants import USERS_GET_URL, USER_DETAIL_CACHE_KEY


class UserListApiView(APIView):
    def get_users(self):
        try:
            users = requests.get(USERS_GET_URL)
            return users.json()
        except Exception:
            raise ServiceUnavailable

    def get(self, request):
        users = self.get_users()
        return JsonResponse(users, safe=False)


class UserDetailApiView(APIView):
    cache_key = USER_DETAIL_CACHE_KEY  # needs to be unique
    cache_time = 86400  # time in seconds for cache to be valid

    def get_object(self, pk):
        user = cache.get(self.cache_key.format(pk))  # returns None if no key-value pair

        if not user:
            try:
                user = requests.get("{0}/{1}/".format(USERS_GET_URL, pk))
                user = user.json()
                cache.set(self.cache_key.format(pk), user, self.cache_time)
                print('from api')
                return user
            except Exception:
                raise NotFound
        else:
            print('from cache')
            return user

    def get(self, request, pk):
        user = self.get_object(pk)
        return JsonResponse(user, safe=False)
