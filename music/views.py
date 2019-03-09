from rest_framework import generics, permissions

from .models import Song
from .serializers import SongSerializer


# Create your views here.
class SongListApiView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        # you can put here business logic that
        # is specific to version 1
        if self.request.version == 'v1':
            return super().list(request, *args, **kwargs)
        # You can put here the current version
        # business logic
        return super().list(request, *args, **kwargs)
