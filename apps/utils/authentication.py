from datetime import datetime, timedelta
import jwt
import uuid
from calendar import timegm

from django.utils.encoding import smart_text
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from django.utils.translation import ugettext as _
from rest_framework import serializers
from rest_framework_jwt.compat import Serializer
from rest_framework_jwt.compat import get_username
from rest_framework_jwt.settings import api_settings

from wx_user.models import WxUser
from .wx_fun import get_openid

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER




def jwt_payload_handler(user, exp=datetime.utcnow() + timedelta(days=60)):
    username_field = "user_name"
    username = get_username(user)

    # warnings.warn(
    #     'The following fields will be removed in the future: '
    #     '`email` and `user_id`. ',
    #     DeprecationWarning
    # )
    payload = {
        'user_id': user.pk,
        'user_name': username,
        'exp': exp
    }
    # if hasattr(user, 'email'):
    #     payload['email'] = user.email
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)

    payload[username_field] = username

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


class WxUserSerializer(Serializer):
    def __init__(self, *args, **kwargs):
        """
        Dynamically add the USERNAME_FIELD to self.fields.
        """
        super(WxUserSerializer, self).__init__(*args, **kwargs)
        self.fields["code"] = serializers.CharField()

    def validate(self, attrs):

        credentials = {
            'code': attrs.get('code')
        }

        if all(credentials.values()):
            try:
                user = WxUser.objects.get(openid=get_openid(credentials.get('code')))
            except WxUser.DoesNotExist:
                msg = _('the validate code is error')
                raise serializers.ValidationError(msg)

            if user:
                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }

            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            # msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """
    def get_jwt_value(self, request):
        pass

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        # User = get_user_model()
        # username = jwt_get_username_from_payload(payload)

        user_id = payload.get('user_id')        # 如果更新用户信息时，则要重新登录获取新的token

        if not user_id:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            # user = User.objects.get_by_natural_key(username)
            user = WxUser.objects.get(id=user_id)
        except WxUser.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        # if not user.is_active:
        #     msg = _('User account is disabled.')
        #     raise exceptions.AuthenticationFailed(msg)

        return user

class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)