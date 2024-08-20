from rest_framework import  exceptions
from rest_framework.response import Response
from accounts.token_checker import TokenErrorHandler
from rest_framework.views import  set_rollback, exception_handler
from django.core.exceptions import PermissionDenied
from django.http import Http404


def custom_exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait
        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'detail': exc.detail}
        set_rollback()
        
        response = Response(data, status=exc.status_code, headers=headers)
        if response.data.get('messages'):
            auth = context['request'].headers.get('Authorization', False)
            if auth:
                token = auth.split()[1]
                message = TokenErrorHandler(token).check()
                data['messages'][0]['message'] = message['msg']
                data['code'] = message['code']
        return response
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status_code'] = response.status_code

    return response