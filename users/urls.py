from django.urls import path
from users import views


urlpatterns = [
    path('users/', views.UserListApiView.as_view()),
    path('users/<int:pk>/', views.UserDetailApiView.as_view()),
]
