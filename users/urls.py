from django.urls import path
from .views import (
    UserListCreateApiView, UserActivateView, UserConfirmView, UserGetConfirmView,
    LoginView, UserRegistrationView
)


urlpatterns = [
    path('users/', UserListCreateApiView.as_view()),
    # path('users/<int:pk>/', UserDetailApiView.as_view()),
    path('users/activate/', UserActivateView.as_view(), name='user-activate'),
    path('users/activate/confirm/', UserConfirmView.as_view(), name='user-confirm'),
    path('users/activate/confirm/<token>/', UserGetConfirmView.as_view(), name='user-get-confirm'),

    path('auth/login/', LoginView.as_view(), name="auth-login"),
    path('auth/register/', UserRegistrationView.as_view(), name="auth-register"),

]
