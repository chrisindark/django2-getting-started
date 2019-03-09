import json

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Song
from .serializers import SongSerializer

from users.models import User


# Create your tests here.
class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_song(title='', artist=''):
        if title != '' and artist != '':
            Song.objects.create(title=title, artist=artist)

    def create_user(self, username, password):
        # create a user
        self.set_up(username=username, password=password)

    def login_a_user(self, username='', password=''):
        self.create_user(username, password)

        url = reverse('auth-login', kwargs={})

        response = self.client.post(url, data=json.dumps({
            'username': username,
            'password': password
        }), content_type='application/json')

        return response

    def login_client(self, username='', password=''):
        self.create_user(username, password)

        # get a token from DRF
        response = self.client.post(
            reverse('create-token'),
            data=json.dumps({
                'username': username,
                'password': password
            }),
            content_type='application/json'
        )

        self.token = response.data['token']
        # set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.token
        )
        # self.client.login(username=username, password=password)
        return self.token

    def set_up(self, username='', password=''):
        # create a admin user
        if username is '':
            username = 'testuser'
        if password is '':
            password = 'testuser'

        self.user = User.objects.create_superuser(
            username=username,
            email='test@test.com',
            password=password,
            first_name='test',
            last_name='user',
        )

        # add test data
        self.create_song('like glue', 'sean paul')
        self.create_song('simple song', 'konshens')
        self.create_song('love is wicked', 'brick and lace')
        self.create_song('jam rock', 'damien marley')


class GetAllSongsTest(BaseViewTest):

    def test_get_all_songs(self):
        """
        This test ensures that all songs added in the setUp method
        exist when we make a GET request to the songs/ endpoint
        """
        # hit the API endpoint
        self.login_client('testuser', 'testuser')
        response = self.client.get(
            reverse('songs', kwargs={'version': 'v1'})
        )
        # fetch the data from db
        expected = Song.objects.all()
        serialized = SongSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthLoginUserTest(BaseViewTest):
    """
    Tests for the auth/login/ endpoint
    """
    def test_login_user_with_valid_credentials(self):
        # test login with valid credentials
        response = self.login_a_user('testuser', 'testuser')
        # assert token key exists
        self.assertIn('token', response.data)
        # assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test login with invalid credentials
        response = self.login_a_user('anonymous', 'pass')
        # assert status code is 400 BAD REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
