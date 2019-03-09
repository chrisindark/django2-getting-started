from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.conf import settings
from django.contrib.auth import authenticate, login

from .models import User
from .constants import ALPHANUMERIC
from .utils import UserEmailManager


class UserSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(read_only=True, required=False)
    # username = serializers.CharField(required=False, validators=[ALPHANUMERIC], max_length=20, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_active', 'is_superuser',)
        read_only_fields = ('username', 'email', 'is_staff', 'is_active', 'is_superuser',)

    # def validate(self, data):
    #     username = data.get('username')
    #     # Check that the username does not already exist
    #     if User.objects.exclude(pk=self.instance.pk).filter(username=username).first():
    #         raise serializers.ValidationError({
    #             'username': 'Username already exists. Please try another.'
    #         })

    #     return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, max_length=255)
    username = serializers.CharField(required=True, validators=[ALPHANUMERIC], max_length=20, min_length=8)
    password = serializers.CharField(write_only=True, required=True, max_length=128, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'confirm_password',)

    def validate(self, data):
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check that the email does not already exist
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'Email already exists. Was it you?'
            })

        # Check that the username does not already exist
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': 'Username already exists. Please try another.'
            })

        # Check that the password entries match
        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords don\'t match.'
            })

        return data

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username')
        )
        user.set_password(validated_data.get('password'))
        # set user as inactive to allow verification of email
        if settings.SEND_ACTIVATION_EMAIL:
            user.is_active = False
        else:
            user.is_active = True
        user.save()

        return user


class UserActivateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    user = None

    class Meta:
        model = User
        fields = ('email',)

    def validate(self, data):
        email = data.get('email', None)
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'Email does not exist.'
            })

        self.user = User.objects.get(email=email)
        if self.user.is_active:
            raise serializers.ValidationError({
                'email': 'Account is already active.'
            })

        return data

    def save(self, **kwargs):
        self.user.security_key, self.user.security_key_expires = UserEmailManager.generate_activation_key()
        request = self.context.get('request')
        subject_template_name = settings.ACCOUNT_ACTIVATION_EMAIL_SUBJECT
        email_template_name = settings.ACCOUNT_ACTIVATION_EMAIL_BODY
        html_email_template_name = settings.ACCOUNT_ACTIVATION_EMAIL_TEMPLATE
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        to_email = self.user.email
        context = {
            'url': settings.ACCOUNT_ACTIVATION_URL,
            'domain': settings.DOMAIN_URL,
            'site_name': settings.SITE_NAME,
            'user': self.user,
            'token': self.user.security_key,
            'protocol': 'https' if request.is_secure() else 'http'
        }

        UserEmailManager.send_email(subject_template_name, email_template_name,
                                    context, from_email, to_email, html_email_template_name)
        self.user.save()

        return self.user


class UserConfirmSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True, required=True)

    user = None

    class Meta:
        model = User
        fields = ('token',)

    def validate(self, data):
        try:
            self.user = User.objects.get(security_key=data['token'])
            if self.user.is_active:
                raise ValidationError('Account is already active.')
            # elif self.user.security_key_expires < datetime.now():
            #     raise ValidationError({'token': 'Expired value'})
        except User.DoesNotExist:
            raise ValidationError({'token': 'Invalid value'})

        return data

    def create(self, validated_data):
        self.user.is_active = True
        self.user.security_key = None
        self.user.security_key_expires = None
        self.user.save()

        return self.user


class TokenSerializer(serializers.Serializer):
    """
    This serializer serializes the token data
    """
    token = serializers.CharField(max_length=255)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, validators=[ALPHANUMERIC], max_length=20, min_length=8)
    password = serializers.CharField(required=True, max_length=128, min_length=8)

    user = None

    def validate(self, data):
        request = self.context.get('request')
        self.user = authenticate(request, **data)
        if self.user is None:
            raise ValidationError({'non_field_errors': 'Unable to log in with provided credentials.'})

        # login saves the user’s ID in the session,
        # using Django’s session framework.
        # login(request, self.user)
        return data

    def save(self, **kwargs):
        return self.user
