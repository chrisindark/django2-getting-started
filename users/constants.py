from django.core.validators import RegexValidator


USERS_GET_URL = 'https://jsonplaceholder.typicode.com/users'

USER_DETAIL_CACHE_KEY = 'USER_DETAIL_CACHE_KEY_{0}'

ALPHANUMERIC = RegexValidator(
    r'^[a-z][a-z0-9]*$',
    'Only lowercase letters and numbers are allowed. Value should start with a letter.'
)
