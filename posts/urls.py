from django.urls import path
from posts import views


urlpatterns = [
    path('posts/', views.PostListApiView.as_view()),
    path('posts/<int:pk>/', views.PostDetailApiView.as_view()),
]
