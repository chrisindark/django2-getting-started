from django.urls import path, re_path

from .views import SongListApiView


urlpatterns = [
    re_path('(?P<version>(v1|v2))/songs/', SongListApiView.as_view(), name="songs")
]
