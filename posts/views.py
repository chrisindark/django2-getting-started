import requests

from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView

from mysite.exceptions import ServiceUnavailable
from .constants import POSTS_GET_URL ,POST_DETAIL_CACHE_KEY


# Create your views here.
class PostListApiView(APIView):
    def get_posts(self):
        try:
            posts = requests.get(POSTS_GET_URL)
            return posts.json()
        except Exception:
            raise ServiceUnavailable

    def get(self, request):
        posts = self.get_posts()
        return JsonResponse(posts, safe=False)


class PostDetailApiView(APIView):
    cache_key = POST_DETAIL_CACHE_KEY  # needs to be unique
    cache_time = 86400  # time in seconds for cache to be valid

    def get_object(self, pk):
        post = cache.get(self.cache_key.format(pk))  # returns None if no key-value pair

        if not post:
            try:
                post = requests.get("{0}/{1}/".format(POSTS_GET_URL, pk))
                post = post.json()
                cache.set(self.cache_key.format(pk), post, self.cache_time)
                print('from api')
                return post
            except Exception:
                raise NotFound
        else:
            print('from cache')
            return post

    def get(self, request, pk):
        post = self.get_object(pk)
        return JsonResponse(post, safe=False)
