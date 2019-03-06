import requests

from django.http import JsonResponse
from django.core.cache import cache

from rest_framework import views, generics, pagination, status, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from mysite.exceptions import ServiceUnavailable
from users.constants import USERS_GET_URL, USER_DETAIL_CACHE_KEY
from users.serializers import (
    UserSerializer, UserRegistrationSerializer, UserActivateSerializer, UserConfirmSerializer
)
from users.models import User
from users.permissions import IsNotAuthenticated


# Create your views here.
class StaticUserListApiView(views.APIView):
    def get_users(self):
        try:
            users = requests.get(USERS_GET_URL)
            return users.json()
        except Exception:
            raise ServiceUnavailable

    def get(self, request):
        users = self.get_users()
        return JsonResponse(users, safe=False)


class StaticUserDetailApiView(views.APIView):
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


class UserPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    # max_page_size = 1000


class UserMixin(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination


class UserListCreateApiView(UserMixin, generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserRegistrationSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.request.method == 'POST':
            return (IsNotAuthenticated(),)
        return (IsNotAuthenticated(),)

    def perform_create(self, serializer):
        serializer.save()
        # uncomment when an email server is installed
        self.send_activation_email(serializer.data)

    def send_activation_email(self, user):
        context = self.get_serializer_context()
        serializer = UserActivateSerializer(data=user, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()


class UserActivateView(generics.CreateAPIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = UserActivateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': 'Account activation email has been sent.'
        }, status=status.HTTP_200_OK)


class UserConfirmView(generics.CreateAPIView, generics.RetrieveAPIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = UserConfirmSerializer

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token', None)
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': 'Your account has been activated.'
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': 'Your account has been activated.'
        }, status=status.HTTP_200_OK)
