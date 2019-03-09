import requests

from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

from rest_framework import views, generics, pagination, status, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings

from mysite.exceptions import ServiceUnavailable
from users.constants import USERS_GET_URL, USER_DETAIL_CACHE_KEY
from users.serializers import (
    UserSerializer, UserRegistrationSerializer, UserActivateSerializer, UserConfirmSerializer,
    LoginSerializer, TokenSerializer
)
from users.models import User
from users.permissions import IsNotAuthenticated


# Get the JWT settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


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

    def send_activation_email(self, user):
        context = self.get_serializer_context()
        serializer = UserActivateSerializer(data=user, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()


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

        if settings.SEND_ACTIVATION_EMAIL:
            # uncomment when an email server is installed
            self.send_activation_email(serializer.data)

        return Response({
            'detail': 'Account activation email has been sent.'
        }, status=status.HTTP_200_OK)


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


class UserConfirmViewMixin(object):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = UserConfirmSerializer


class UserConfirmView(UserConfirmViewMixin, generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': 'Your account has been activated.'
        }, status=status.HTTP_200_OK)


class UserGetConfirmView(UserConfirmViewMixin, generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=kwargs)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'detail': 'Your account has been activated.'
        }, status=status.HTTP_200_OK)


class LoginView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user is not None:
            serializer = TokenSerializer(data={
                # using drf jwt utility functions to generate a token
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid()
            return Response(serializer.validated_data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserRegistrationView(UserMixin, generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if settings.SEND_ACTIVATION_EMAIL:
            # uncomment when an email server is installed
            self.send_activation_email(serializer.data)

        return Response({
            'detail': 'Account activation email has been sent.'
        }, status=status.HTTP_200_OK)
