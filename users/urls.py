from django.urls import path
from .views import UserListCreateApiView, UserActivateView, UserConfirmView


urlpatterns = [
    path('users/', UserListCreateApiView.as_view()),
    # path('users/<int:pk>/', UserDetailApiView.as_view()),
    path('users/activate/', UserActivateView.as_view(), name='user-activate'),
    path('users/activate/confirm/<token>', UserConfirmView.as_view(), name='user-confirm'),
]
