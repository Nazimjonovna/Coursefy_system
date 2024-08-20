from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from jwt import ExpiredSignatureError

User = get_user_model()


class TokenErrorHandler:
    def __init__(self, token):
        self.token = token

    def check(self):
        try:
            jwt_token = self.token
            jwt_payload = self.get_payload(jwt_token)
            user_credentials = self.get_user_credentials(jwt_payload)
            user = self.get_logged_in_user(user_credentials)
            return True
        except ExpiredSignatureError:
            return {"msg": "Expired Token", "code": "token_expired"}
        except:
            return {"msg": "Invalid Token", "code": "token_not_valid"}

    def get_payload(self, jwt_token):
        payload = jwt_decode(
            jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload

    def get_user_credentials(self, payload):
        user_id = payload['user_id']
        return user_id

    async def get_logged_in_user(self, user_id):
        user = await self.get_user(user_id)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
