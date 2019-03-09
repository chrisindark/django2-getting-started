from rest_framework import generics, permissions, status

from rest_framework.response import Response

from .models import Song
from .serializers import SongSerializer
from .decorators import validate_request_data


# Create your views here.
class SongListCreateApiView(generics.ListCreateAPIView):
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

    @validate_request_data
    def post(self, request, *args, **kwargs):
        song = Song.objects.create(
            title=request.data['title'],
            artist=request.data['artist']
        )
        return Response(
            data=SongSerializer(song).data,
            status=status.HTTP_201_CREATED
        )


class SongsDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    def get(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            return Response(
                data=SongSerializer(song).data,
                status=status.HTTP_200_OK
            )
        except Song.DoesNotExist:
            return Response(
                data={
                    'message': 'Song with id: {0} does not exist'.format(kwargs['pk'])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    @validate_request_data
    def put(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            serializer = SongSerializer()
            updated_song = serializer.update(song, request.data)
            return Response(SongSerializer(updated_song).data)
        except Song.DoesNotExist:
            return Response(
                data={
                    'message': 'Song with id: {0} does not exist'.format(kwargs['pk'])
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            song = self.queryset.get(pk=kwargs['pk'])
            song.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Song.DoesNotExist:
            return Response(
                data={
                    'message': 'Song with id: {0} does not exist'.format(kwargs['pk'])
                },
                status=status.HTTP_404_NOT_FOUND
            )
