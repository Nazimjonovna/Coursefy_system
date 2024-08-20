from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import  TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from accounts.signals import add_entry_info, update_last_login


class TokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        data['user_id'] = self.user.id

        # User token bilan login qilgan userni entry_data sini HisotryOfEntries modeliga qo'shish
        request = self.context.get('request')
        user = self.user
        add_entry_info(request, user)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

class TokenObtainPairVieww(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = TokenObtainPairSerializer