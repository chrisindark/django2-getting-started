from django.urls import re_path

from .views import SongListCreateApiView, SongsDetailApiView


urlpatterns = (
    re_path('(?P<version>(v1|v2))/songs/$', SongListCreateApiView.as_view(), name='songs'),
    re_path('(?P<version>(v1|v2))/songs/(?P<pk>\d+)/$', SongsDetailApiView.as_view(), name='songs-detail'),
)
