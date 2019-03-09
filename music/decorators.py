from rest_framework.response import Response

from rest_framework import status


def validate_request_data(fn):
    def decorated(*args, **kwargs):
        # args[0] == GenericView Object
        title = args[0].request.data.get('title', '')
        artist = args[0].request.data.get('artist', '')
        if not title or not artist:
            return Response(
                data={
                    'message': 'Both title and artist are required to add a song'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return fn(*args, **kwargs)
    return decorated
